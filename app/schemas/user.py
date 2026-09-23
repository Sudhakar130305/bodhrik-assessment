from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    PARENT = "parent"
    STUDENT = "student"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    parent_id: int | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    parent_id: int | None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str