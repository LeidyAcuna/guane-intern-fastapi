from typing import Any, List, Generator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from . import actions, models, schemas
from .db import SessionLocal, engine

# Create all tables in database.
# Comment this out if you using migrations.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session.
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# User API
@app.get("/api/users", response_model=List[schemas.User], tags=["users"])
def list_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    users = actions.user.get_all(db=db, skip=skip, limit=limit)
    return users


@app.post(
        "/api/users",
        response_model=schemas.User,
        status_code=HTTP_201_CREATED,
        tags=["users"])
def create_users(*, db: Session = Depends(get_db), user_obj: schemas.UserCreate) -> Any:
    user = actions.user.get_email(db=db, email=user_obj.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    print
    user = actions.user.create(db=db, user=user_obj)
    return user


@app.put(
        "/api/users/{email}", response_model=schemas.User,
        responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
        tags=["users"])
def update_user(
                *, db: Session = Depends(get_db),
                email: str,
                user_obj: schemas.UserUpdate) -> Any:
    user = actions.user.get_email(db=db, email=email)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    user = actions.user.update(db=db, db_obj=user, obj_in=user_obj)
    return user


@app.delete("/api/users/{email}", response_model=schemas.User,
            responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
            tags=["users"])
def delete_users(*, db: Session = Depends(get_db), email: str) -> Any:
    user = actions.user.get_email(db=db, email=email)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    user = actions.user.remove(db=db, email=email)
    return user


# Dog API
@app.get("/api/dogs", response_model=List[schemas.Dog], tags=["dogs"])
def list_dogs(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> Any:
    dogs = actions.dog.get_all(db=db, skip=skip, limit=limit)
    return dogs


@app.get("/api/dogs/is_adopted", response_model=List[schemas.Dog], tags=["dogs"])
def list_dogs_adopted(
                    db: Session = Depends(get_db),
                    skip: int = 0,
                    limit: int = 100) -> Any:
    dogs = actions.dog.get_adopted(db=db, skip=skip, limit=limit)
    return dogs


@app.get(
        "/api/dogs/{name}", response_model=schemas.Dog,
        responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
        tags=["dogs"])
def get_dog(*, db: Session = Depends(get_db), name: str) -> Any:
    dog = actions.dog.get_name(db=db, name=name)
    if not dog:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Dog not found")
    return dog


@app.post(
        "/api/users/{user_email}/dogs/",
        response_model=schemas.Dog,
        status_code=HTTP_201_CREATED,
        tags=["dogs"])
def create_dog_for_user(
                        *, db: Session = Depends(get_db),
                        dog_obj: schemas.DogCreate,
                        email: str) -> Any:
    dog = actions.dog.create_dog_user(db=db, obj_in=dog_obj, email=email)
    return dog


@app.put(
        "/api/dogs/{name}", response_model=schemas.Dog,
        responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
        tags=["dogs"])
def update_dog(
                *, db: Session = Depends(get_db), name: str, dog_obj: schemas.DogUpdate,
                ) -> Any:
    dog = actions.dog.get_name(db=db, name=name)
    if not dog:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Dog not found")
    dog = actions.dog.update(db=db, db_obj=dog, obj_in=dog_obj)
    return dog


@app.delete("/api/dogs/{name}", response_model=schemas.Dog,
            responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
            tags=["dogs"])
def delete_dogs(*, db: Session = Depends(get_db), name: str) -> Any:
    dog = actions.dog.get_name(db=db, name=name)
    if not dog:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Dog not found")
    dog = actions.dog.remove(db=db, name=name)
    return dog
