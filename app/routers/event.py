from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.user import Event, User, Group
from app.routers.auth import get_current_user
from app.schema import CreateEventSchema, EventResponseModel
from typing import Literal, Annotated
from sqlalchemy import select
from sqlalchemy.orm import joinedload

event_router = APIRouter(prefix="/events", tags=["events"])


async def get_authorized_event(
    event_id: UUID, user: Annotated[User, Depends(get_current_user)]
) -> Event:
    event = await Event.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"event with id {event_id} not found",
        )
    group = await Group.get_by_id(event.group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"group of event with id {event_id} not found",
        )
    if not await group.is_member(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "you can't access an event you don't own "
                "or an event from a group you don't belong to"
            ),
        )
    return event


@event_router.post(
    "", response_model=EventResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_event(
    body: CreateEventSchema, user: Annotated[User, Depends(get_current_user)]
):
    event = await Event.new(**body.model_dump())
    return {"message": "event successfully created!", "data": event}


@event_router.get("")
async def get_events(
    user: Annotated[User, Depends(get_current_user)],
    filter_by: Literal["authored", "membership"] = "authored",
    db: AsyncSession = Depends(get_session),
):
    query = select(User).where(User.id == user.id).options(joinedload(User.groups))
    user_with_groups = (await db.execute(query)).unique().scalar_one_or_none()
    if not user_with_groups:
        # user belongs to no group, return empty list
        ...


@event_router.get("/{event_id}", response_model=EventResponseModel)
async def get_one_event(event: Event = Depends(get_authorized_event)):
    return {"message": "event successfully retrieved!", "data": event}


@event_router.patch("/{event_id}")
async def update_event(event: Event = Depends(get_authorized_event)):
    ...


@event_router.get("/{event_id}/rsvp")
async def rsvp_event(event: Event = Depends(get_authorized_event)):
    ...
