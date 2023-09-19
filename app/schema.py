from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr


class BaseResponseSchema(BaseModel):
    message: str


class AccessTokenSchema(BaseModel):
    access_token: str
    type: Literal["bearer"] = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMj"
                    "M0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2M"
                    "jM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
                ),
                "type": "bearer",
            }
        }


class SignUpSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "password": "password123",
                "confirm_password": "password123",
            }
        }


class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    username: str | None
    display_name: str | None
    profile_image_url: str | None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "",
                "email": "johndoe@example.com",
                "username": "@johnydoe99",
                "display_name": "John",
                "profile_image_url": "https://127.0.0.1/assets/image1.png",
            }
        }


class UpdateUserSchema(BaseModel):
    username: str | None
    display_name: str | None


class GetAccessTokenResponseSchema(BaseResponseSchema):
    data: AccessTokenSchema

    class Config:
        json_schema_extra = {
            "example": {
                "message": "access token successfully retrieved!",
                "data": AccessTokenSchema.Config.json_schema_extra["example"],
            }
        }


class GetUserResponseSchema(BaseResponseSchema):
    data: UserSchema


class UpdateUserResponseSchema(BaseResponseSchema):
    data: UserSchema
