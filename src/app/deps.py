from typing import Optional

import jwt

from app.logger import logger
from app.models import User
from app.settings import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify-otp", auto_error=False)
oauth2_scheme_ums = OAuth2PasswordBearer(tokenUrl="/auth/register", auto_error=False)


class TokenData(BaseModel):
    user_id: Optional[int]
    email: Optional[str]
    is_signup_complete: Optional[bool]


def get_current_user(
        db=Depends(settings.get_repo), token: str = Depends(oauth2_scheme)
) -> User:
    logger.info(token)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if not token:
            raise credentials_exception
        payload = {}  # decode_auth_token(auth_token=token)
        logger.info(payload)

        token_data = TokenData(**payload)

    except jwt.InvalidTokenError as e:
        raise credentials_exception from e
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user
