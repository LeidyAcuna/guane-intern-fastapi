from typing import Optional

from pydantic import UUID4, BaseModel


class HTTPError(BaseModel):
    detail: str


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

    class Config:
        orm_mode = True


# Additional properties to return via API
class Dog(DogInDBBase):
    pass


# Additional properties stored in DB
class DogInDB(DogInDBBase):
    pass
