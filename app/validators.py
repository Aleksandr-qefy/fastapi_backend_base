import re
import uuid
from typing import Union

import pydantic
import pydantic_core


def check_email(email: str) -> Union[str, None]:
    try:
        _, email = pydantic.validate_email(email)
        email = email.lower()
    except pydantic_core.PydanticCustomError:
        return None
    return email


nickname_reg = re.compile('^[a-zA-Z0-9_-]+$')
def check_nickname(nickname: str) -> bool:
    if len(nickname) < 4 or len(nickname) > 30:
        return False
    return bool(nickname_reg.match(nickname))


password_reg = re.compile('^[a-zA-Z0-9!@#$%^&*()_+\-={}\[\]|;:\'\",.<>/?]+$')
def check_password(password: str) -> bool:
    if len(password) < 8 or len(password) > 100:
        return False
    return bool(password_reg.match(password))


def check_uuid(uuid_str: str) -> bool:
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False




