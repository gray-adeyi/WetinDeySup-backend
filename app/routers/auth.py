from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app.models.user import User
from app.schema import GetAccessTokenResponseSchema, SignUpSchema, BaseResponseSchema
from app.settings import default_settings
from app.utils import create_access_token, get_password_hash

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/access-token",
)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            default_settings.JWT_SETTINGS.SECRET_KEY,
            algorithms=[default_settings.JWT_SETTINGS.ALGORITHM],
        )
        user_id: str = payload.get("subject").get("user_id")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await User.get_by_id(UUID(user_id))
    if not user:
        raise credentials_exception
    return user


@auth_router.post("/sign-up", response_model=BaseResponseSchema)
async def sign_up(body: SignUpSchema):
    """
    This endpoint starts the user onboarding process, it allows the creation
    of `User` on our backend. after which the `/access-token` endpoint is hit
    to retrieve the `access-token` that allows us to access protected endpoints.
    For the sake of simplicity. we bypass the email verification process
    """
    hashed_password = get_password_hash(body.confirm_password)
    await User.new(email=body.email, password=hashed_password)
    return {
        "message": (
            "sign up successful! hit the /access-token endpoint "
            "to obtain the access token for the newly signed up user"
        )
    }


@auth_router.post("/access-token", response_model=GetAccessTokenResponseSchema)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    This endpoint allows you to retrieve the access token for a user

    Note:
         The user's email should be provided in the username field when using the
         swagger docs.
    """
    # TODO: Provide both refresh and access token
    user = await User.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=default_settings.JWT_SETTINGS.EXPIRES_DELTA
    )
    token_data = {
        "subject": {
            "user_id": str(user.id),
        }
    }
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    return {
        "message": "access token successfully retrieved!",
        "data": {"access_token": access_token, "token_type": "bearer"},
    }
