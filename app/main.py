from typing import Union

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import config
import crud
import schemas
from database import SessionLocal, Base, engine
from validators import check_email, check_uuid, check_nickname, check_password
from email_sending import EmailRegistration, send_email
import jwt_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executed before the application starts
    Base.metadata.create_all(engine)
    yield
    # Executed after the application starts
    # ...

app = FastAPI(lifespan=lifespan)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


def get_db(request: Request):
    return request.state.db


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/delete/", response_model=schemas.OkMsg)
def users_delete(nickname: str, db: Session = Depends(get_db)):
    if check_nickname(nickname):
        user = crud.get_user_by_nickname(db, nickname)
        if user:
            # print(user.id)
            crud.delete_user(db, user)
            return schemas.OkMsg()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname is not in DB")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname is not valid")


@app.post("/me/", response_model=schemas.UserSettings)
def show_settings_to_user(token: schemas.Token, request: Request, db: Session = Depends(get_db)):
    # print(request.values())
    user = jwt_module.get_user_by_token(db, token.access_token)
    return schemas.UserSettings(nickname=user.nickname, email=user.email)


def authenticate_user(db: Session, nick_or_email: str, password: str) -> Union[schemas.User, None]:
    if not check_password(password):
        # password is not valid
        return None

    user = None

    email = check_email(nick_or_email)
    if email:
        user = crud.log_in_by_password_and_email(db, password, email)

    if not user and check_nickname(nick_or_email):
        user = crud.log_in_by_password_and_nickname(db, password, nick_or_email)
    # if user == None: invalid email/nickname or wrong email/nickname
    return user


@app.post("/users/login/", response_model=schemas.Token)
def user_login(user_login_obj: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login_obj.nick_or_email, user_login_obj.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email/nick or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return jwt_module.get_token_by_user(user)


@app.post("/users/token_update/", response_model=schemas.Token)
def user_token_update(token: schemas.Token, db: Session = Depends(get_db)):
    return jwt_module.get_token_by_user(jwt_module.get_user_by_token(db, token.access_token))


@app.post("/users/create/", response_model=schemas.OkMsg)
def create_user_unconfirmed(user: schemas.UserCreate, db: Session = Depends(get_db)):
    email = check_email(user.email)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is not valid")
    user.email = email

    user_confirmed = crud.get_user_by_email(db, email=user.email)
    if user_confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Сan't create two accounts for the same email")

    if not check_nickname(user.nickname):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname is not valid")

    print(f"'{user.password}'")
    if not check_password(user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is not valid")

    user_confirmed = crud.get_user_by_nickname(db, nickname=user.nickname)
    if user_confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname already registered")

    user_unconfirmed = crud.create_user_unconfirmed(db=db, user=user)
    link_to_confirm = config.FRONTEND_CLIENT + f"user/{user_unconfirmed.id}/"
    email_to_confirm = EmailRegistration(
        user.email,
        link_to_confirm
    )
    send_email(email_to_confirm)
    # return user_unconfirmed
    return schemas.OkMsg()


@app.get("/users/unconfirmed/", response_model=list[schemas.UserUnconfirmed])
def read_users_unconfirmed(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users_unconfirmed = crud.get_users_unconfirmed(db, skip=skip, limit=limit)
    return users_unconfirmed


@app.get("/email/registration/{user_unconfirmed_id}", response_model=schemas.Token)
def create_user(user_unconfirmed_id: str, db: Session = Depends(get_db)):
    if check_uuid(user_unconfirmed_id):
        user_unconfirmed = crud.get_user_unconfirmed(db, user_unconfirmed_id)
        if user_unconfirmed:
            if crud.get_user_by_nickname_or_email(db, user_unconfirmed.nickname, user_unconfirmed.email):
                crud.delete_user_unconfirmed(db=db, user_unconfirmed=user_unconfirmed)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Has appeared user with such nickname/email. Try to use another nickname/email")
            user = crud.create_user(db=db, user=user_unconfirmed)
            crud.delete_user_unconfirmed(db=db, user_unconfirmed=user_unconfirmed)
            # return user
            return jwt_module.get_token_by_user(user)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No user with such ID in unconfirmed users. Probably, was confirmed")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
