from typing import Any, List, Generator, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from . import actions, models, schemas
from .db import SessionLocal, engine

from datetime import datetime, timedelta

# Create all tables in database.
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "049780c990542fbae7050cf0d2e9e0115d591e2fed7ecb010a360bdb56ba7231"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
        "leidyacuna": {
            "username": "leidyacuna",
            "fullname": "Leidy Acuña",
            "email": "leidyacuna@gmail.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "disabled": False,
        }
    }


app = FastAPI()


# Dependency to get DB session.
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Auth actions
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.UserAuthBase = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserAuthInDB(**user_dict)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Auth
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user_auth/me")
async def read_user_me(current_user: schemas.UserAuthBase = Depends(get_current_user)):
    return current_user


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
def create_users(*, db: Session = Depends(get_db),
                 user_obj: schemas.UserCreate,
                 current_user: schemas.UserAuthBase = Depends(get_current_user)) -> Any:
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
                user_obj: schemas.UserUpdate,
                current_user: schemas.UserAuthBase = Depends(get_current_user)) -> Any:
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
                        *,
                        db: Session = Depends(get_db),
                        dog_obj: schemas.DogCreate,
                        email: str,
                        current_user: schemas.UserAuthBase = Depends(get_current_user)
                        ) -> Any:
    user = actions.user.get_email(db=db, email=email)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    id = user.id
    dog = actions.dog.create_dog_user(db=db, obj_in=dog_obj, id=id)
    return dog


@app.put(
        "/api/dogs/{name}", response_model=schemas.Dog,
        responses={HTTP_404_NOT_FOUND: {"model": schemas.HTTPError}},
        tags=["dogs"])
def update_dog(
                *, db: Session = Depends(get_db),
                name: str,
                dog_obj: schemas.DogUpdate,
                current_user: schemas.UserAuthBase = Depends(get_current_user)) -> Any:
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
