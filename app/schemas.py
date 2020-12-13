from typing import Optional, List

from pydantic import UUID4, BaseModel


class HTTPError(BaseModel):
    detail: str


# Auth Model
class UserAuthBase(BaseModel):
    username: str
    email: Optional[str] = None
    fullname: Optional[str] = None
    disabled: Optional[bool] = None


class UserAuthInDB(UserAuthBase):
    hashed_password: str


# Token Model
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Dog schema
# Shared properties
class DogBase(BaseModel):
    name: Optional[str] = None
    is_adopted: Optional[bool] = None


# Properties to receive via API on creation
class DogCreate(DogBase):
    name: str
    is_adopted: bool


# Properties to receive via API on update
class DogUpdate(DogBase):
    pass


class DogInDBBase(DogBase):
    picture: Optional[str] = None
    create_date: Optional[str] = None
    id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Dog(DogInDBBase):
    pass


# Additional properties stored in DB
class DogInDB(DogInDBBase):
    pass


# User schema
# Shared properties
class UserBase(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    name: str
    lastname: str
    email: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[UUID4] = None
    dogs: List[Dog] = []

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    pass
