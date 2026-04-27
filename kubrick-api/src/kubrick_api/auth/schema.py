from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")

    model_config = ConfigDict(
         json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securePassword123",
                "full_name": "John Doe",
            }
        }
    )

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User Password")

    model_config= ConfigDict(
        json_schema_extra={
            "example":{
                "email": "user@example.com",
                "password":"securepassword123"
            }
        }
    )

class UserResponse(UserBase):
    id: int = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    model_config = ConfigDict(from_attributes=True)

###Token Schemas

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Token expiration in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token (optional)")

    model_config = ConfigDict(
        json_schema_extra={
            "example":{
                "acess_token": "eydajbjbdsadkmknasda",
                "expires_in": 1800,
                "refresh_token":"eyhdshhha"
            }
        }
    )

class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., description="Refresh token from login response")

class TokenPayload(BaseModel):
    sub: int = Field(..., description="Subject: user ID")
    email: str = Field(..., description="User email")
    exp:int = Field(..., description="Expiration time")
    iat: int = Field(..., description="Issued at time")
    type: str= Field(default="access", description="Token type: access or refresh")


class ErrorResponse(BaseModel):
    status_code: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Internal error code")

    model_config = ConfigDict(
        json_schema_extra={
            "example":{
                "status_code": 401,
                "detail":"Invalid credentials",
                "error_code": "INVALID_CREDENTIALS"
            }
        }
    )

    ####Success response

class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success Message")
    data: Optional[dict] = Field(None, description="Response data")