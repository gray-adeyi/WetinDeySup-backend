from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.models.user import User, Group
from app.routers.auth import get_current_user
from app.schema import (
    CreateGroupSchema,
    CreateUserGroupResponseSchema,
    GetUserGroupsResponseSchema,
    UserIDsSchema,
)

group_router = APIRouter(prefix="/groups", tags=["groups"])


async def group_must_belong_to_current_user(
    group_id: UUID, user: Annotated[User, Depends(get_current_user)]
):
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"group id {group_id}")
    group = await Group.get_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"group with id {group_id} not found",
        )
    if group.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"group with id {group.id} does not belong to {user.id}",
        )
    return group


@group_router.post(
    "",
    response_model=CreateUserGroupResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_group(
    body: CreateGroupSchema, user: Annotated[User, Depends(get_current_user)]
):
    new_group = await Group.new(author_id=user.id, **body.model_dump())
    return {"message": "group successfully created!", "data": new_group}


@group_router.get("", response_model=GetUserGroupsResponseSchema)
async def get_user_groups(
    user: Annotated[User, Depends(get_current_user)],
    filter_by: Literal["authored", "membership"] = "authored",
    db: AsyncSession = Depends(get_session),
):
    query = select(Group)
    # retrieve groups that belong to the current user
    if filter_by == "authored":
        query = select(Group).where(Group.author_id == user.id)
    # retrieve groups that the current user is a member of
    if filter_by == "membership":
        query = select(Group).where(Group.members.any(id == user.id))
    result = (await db.execute(query)).scalars().all()
    return {"message": "groups successfully retrieved!", "data": result}


@group_router.get("/{group_id}")
async def get_one_user_group(group: Group = Depends(group_must_belong_to_current_user)):
    return group


@group_router.patch("/{group_id}")
async def update_user_group(
    user: Annotated[User, Depends(get_current_user)],
    group: Group = Depends(group_must_belong_to_current_user),
):
    ...


@group_router.patch("/{group_id}/update-cover-image")
async def update_cover_image(
    cover_image: UploadFile,
    user: Annotated[User, Depends(get_current_user)],
    group: Group = Depends(group_must_belong_to_current_user),
):
    ...


@group_router.patch("/{group_id}/add-group-members")
async def add_group_members(
    body: UserIDsSchema,
    user: Annotated[User, Depends(get_current_user)],
    group: Group = Depends(group_must_belong_to_current_user),
    db: AsyncSession = Depends(get_session),
):
    new_members: list[User] = []
    for user_id in body.user_ids:
        member = await User.get_by_id(user_id)
        if not member:
            continue
        if await user.is_a_follower(member.id):
            new_members.append(member)

    query = select(Group).where(Group.id == group.id).options(joinedload(Group.members))
    group_with_members = (await db.execute(query)).scalar_one_or_none()
    group_with_members.members.append(*new_members)
    db.add(group_with_members)
    await db.commit()
    await db.refresh(group_with_members)
    return group_with_members


@group_router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_group(group: Group = Depends(group_must_belong_to_current_user)):
    await group.delete()
