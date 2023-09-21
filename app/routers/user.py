from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.models.user import User
from app.routers.auth import get_current_user
from app.schema import GetUserResponseSchema, UpdateUserSchema, UpdateUserResponseSchema

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("", response_model=GetUserResponseSchema)
async def get_user(user: Annotated[User, Depends(get_current_user)]):
    return {"message": "user successfully retrieved!", "data": user}


@user_router.patch("", response_model=UpdateUserResponseSchema)
async def update_user(
    body: UpdateUserSchema, user: Annotated[User, Depends(get_current_user)]
):
    user.username = body.username or user.username
    user.display_name = body.display_name or user.display_name
    user = await user.save()
    return {
        "message": "user successfully updated!",
        "data": user,
    }


@user_router.post("/update-profile-image", response_model=UpdateUserResponseSchema)
async def update_profile_image(
    profile_image: UploadFile, user: Annotated[User, Depends(get_current_user)]
):
    ...
