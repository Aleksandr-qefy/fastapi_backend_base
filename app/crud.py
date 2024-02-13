from sqlalchemy.orm import Session
from sqlalchemy import or_

import models, schemas, password_hashing


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_unconfirmed(db: Session, user_unconfirmed_id: str):
    return db.query(models.UserUnconfirmed).filter(models.UserUnconfirmed.id == user_unconfirmed_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_nickname(db: Session, nickname: str):
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def get_user_by_nickname_or_email(db: Session, nickname: str, email: str):
    return db.query(models.User).filter(
        or_(models.User.nickname == nickname, models.User.nickname == email)).first()


def log_in_by_password_and_email(db: Session, password: str, email: str):
    user = get_user_by_email(db, email)
    if user and password_hashing.verify_password(user.hashed_password, password):
        return user
    return None


def log_in_by_password_and_nickname(db: Session, password: str, nickname: str):
    user = get_user_by_nickname(db, nickname)
    if user and password_hashing.verify_password(user.hashed_password, password):
        return user
    return None


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_users_unconfirmed(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserUnconfirmed).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserUnconfirmed):
    # hashed_password = password_hashing.hash_password(user.password)
    db_user = models.User(email=user.email, nickname=user.nickname, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_unconfirmed(db: Session, user: schemas.UserCreate):
    hashed_password = password_hashing.hash_password(user.password)
    db_user = models.UserUnconfirmed(email=user.email, nickname=user.nickname, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user_unconfirmed(db: Session, user_unconfirmed: schemas.UserUnconfirmed):
    user = db.query(models.UserUnconfirmed).filter(models.UserUnconfirmed.id == user_unconfirmed.id).first()
    db.delete(user)
    db.commit()


def delete_user(db: Session, user: schemas.User):
    user = db.query(models.User).filter(models.User.id == user.id).first()
    db.delete(user)
    db.commit()
