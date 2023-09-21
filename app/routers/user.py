from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.models.user import User
from app.routers.auth import get_current_user
from app.schema import (
    GetUserResponseSchema,
    UpdateUserSchema,
    UpdateUserResponseSchema,
    UserListResponseSchema,
    BaseResponseSchema,
    UserIDSchema,
)

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


@user_router.get("/followers", response_model=UserListResponseSchema)
async def get_user_followers(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    """
    This endpoint retrieves a list of `User` that follows
    the current user identified by the access_token
    """
    query = select(User).where(User.id == user.id).options(joinedload(User.followers))
    user_with_followers = (await db.execute(query)).unique().scalar_one()
    return {
        "message": "followers successfully retrieved!",
        "data": user_with_followers.followers,
    }


@user_router.get("/followees", response_model=UserListResponseSchema)
async def get_user_followees(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    """
    This endpoint retrieves a list of `User` that the current
    user identified by the access_token, follows
    """
    query = select(User).where(User.id == user.id).options(joinedload(User.followees))
    user_with_followees = (await db.execute(query)).unique().scalar_one()
    return {
        "message": "followees successfully retrieved!",
        "data": user_with_followees.followees,
    }


@user_router.get("/all-users", response_model=UserListResponseSchema)
async def get_all_users(
    user: Annotated[User, Depends(get_current_user)],
):
    """This endpoint retrieves all the user on the platform."""
    # TODO: Pagination
    all_users = await User.all()
    return {"message": "users successfully retrieved!", "data": all_users}


@user_router.post("/follow", response_model=BaseResponseSchema)
async def follow_user(
    body: UserIDSchema,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    user_to_follow = await User.get_by_id(body.user_id)
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "the user to be followed was not "
                "found. please provide a valid user_id"
            ),
        )
    query = select(User).where(User.id == user.id).options(joinedload(User.followees))
    user_with_followees = (await db.execute(query)).unique().scalar_one()
    if user_to_follow.id not in [user.id for user in user_with_followees.followees]:
        user_with_followees.followees.append(user_to_follow)
    db.add(user_with_followees)
    await db.commit()
    return {"message": f"{user_with_followees.id} now follows {body.user_id}"}


@user_router.post("/unfollow")
async def unfollow_user(
    body: UserIDSchema,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    user_to_unfollow = await User.get_by_id(body.user_id)
    if not user_to_unfollow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "the user to be unfollowed was not "
                "found. please provide a valid user_id"
            ),
        )
    query = select(User).where(User.id == user.id).options(joinedload(User.followees))
    user_with_followees = (await db.execute(query)).unique().scalar_one()

    resulting_followees = [
        user for user in user_with_followees.followees if user.id != user_to_unfollow.id
    ]
    user_with_followees.followees = resulting_followees
    db.add(user_with_followees)
    await db.commit()
    return {"message": f"{user_with_followees.id} has unfollowed {body.user_id}"}
