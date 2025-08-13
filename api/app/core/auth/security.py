from datetime import datetime
from typing import Any

import bcrypt
import jwt
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(subject: str | Any, secret_key: str, expire: datetime) -> str:
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, secret_key, algorithm=settings.TOKEN.ALGORITHM)


def decode_token(token: str, secret_key: str) -> dict[str, Any]:
    payload = jwt.decode(token, secret_key, algorithms=[settings.TOKEN.ALGORITHM])
    return payload


def get_password_hash(password: str, using_bcrypt: bool = False) -> str:
    if not using_bcrypt:
        return pwd_context.hash(password)

    # https://stackoverflow.com/a/77899004/9766354
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode("utf8")
    return string_password


def verify_password(plain_password: str, hashed_password: str, using_bcrypt: bool = False) -> bool:
    if not using_bcrypt:
        pwd_context.verify(plain_password, hashed_password)

    # https://stackoverflow.com/a/77899004/9766354
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_byte_enc = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_byte_enc)
