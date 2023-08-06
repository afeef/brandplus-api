from app.logger import logger
from app.models import User
from app.settings import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/token", auto_error=False)


def get_current_user(
        repo=Depends(settings.get_repo), token: str = Depends(oauth2_scheme)
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

        auth_token = token.replace('Bearer ', '')
        user = repo.validate_access_token(token=auth_token)

        if not user:
            raise credentials_exception
        return user
    except Exception as e:
        raise credentials_exception from e


def get_current_user_from_refresh_token(
        repo=Depends(settings.get_repo), token: str = Depends(oauth2_scheme)
) -> str:
    logger.info(token)

    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = token.replace('Bearer', '')
        user = repo.validate_refresh_token(refresh_token=token)

        if not user:
            raise token_exception

        return user

    except Exception as e:
        raise token_exception from e
