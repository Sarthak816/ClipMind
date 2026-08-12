from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    displayName: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    displayName: str
    role: str
    status: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    user: UserResponse
    accessToken: str
