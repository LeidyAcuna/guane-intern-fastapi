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
        "/api/dogs",
        response_model=schemas.Dog,
        status_code=HTTP_201_CREATED,
        tags=["dogs"])
def create_dogs(*, db: Session = Depends(get_db), post_in: schemas.DogCreate) -> Any:
    dog = actions.dog.create(db=db, obj_in=post_in)
    return dog


@app.put(
        "/api/dogs/{name}", response_model=schemas.Dog,
        responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
        tags=["dogs"])
def update_dog(
                *, db: Session = Depends(get_db), name: str, post_in: schemas.DogUpdate,
                ) -> Any:
    dog = actions.dog.get_name(db=db, name=name)
    if not dog:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Dog not found")
    dog = actions.dog.update(db=db, db_obj=dog, obj_in=post_in)
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
