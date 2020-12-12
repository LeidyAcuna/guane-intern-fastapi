from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import schemas
from .db import Base
from .models import Dog
from . import helpers

from datetime import datetime


# Define custom types for SQLAlchemy model, and Pydantic schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseActions(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """Base class that can be extend by other action classes.
           Provides basic CRUD and listing operations.

        :param model: The SQLAlchemy model
        :type model: Type[ModelType]
        """
        self.model = model

    def get_all(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_name(self, db: Session, name: str) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.name == name).first()

    def get_adopted(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).filter(self.model.is_adopted.is_(True)).all()

    def create(self, db: Session, *, obj_in: schemas.DogCreate) -> ModelType:
        url_image = helpers.getPicture()
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        dog_obj = schemas.DogInDBBase(
                                        **obj_in.dict(),
                                        picture=url_image,
                                        create_date=create_date)
        obj_in_data = jsonable_encoder(dog_obj)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, name: str) -> ModelType:
        dog_delete = db.query(self.model).filter(self.model.name == name).first()
        obj = db.query(self.model).get(dog_delete.id)
        db.delete(obj)
        db.commit()
        return obj


class DogActions(BaseActions[Dog, schemas.DogCreate, schemas.DogUpdate]):
    """Dogs actions with basic CRUD operations"""

    pass


dog = DogActions(Dog)
