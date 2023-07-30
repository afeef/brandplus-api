import logging
import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional, Dict, Union

import jwt

from app.settings import settings


class TokenTypeInvalidError(Exception):
    message = "Token type provided is invalid."

    def __str__(self):
        return TokenTypeInvalidError.message


class TokenTypeEnum(StrEnum):
    ACCESS_TOKEN = 'access'
    REFRESH_TOKEN = 'refresh'

    def __repr__(self):
        return self.value


class Token:
    def __init__(self, token_type: str, token: str, jti: str):
        self.token_type = token_type
        self.token = token
        self.jti = jti


class AuthJWT:
    def __init__(self, algorithm='HS256'):
        self._access_token_expires = settings.access_token_expire
        self._refresh_token_expires = settings.refresh_token_expire
        self._algorithm = algorithm

    def _create_jwt_identifier(self) -> str:
        self.jti = str(uuid.uuid4().hex)
        return self.jti

    def get_jwt_identifier(self) -> str:
        return self.jti

    @staticmethod
    def _get_int_from_datetime(value: datetime) -> int:
        """
        :param value: datetime with or without timezone, if don't contains timezone
                      it will managed as it is UTC
        :return: Seconds since the Epoch
        """
        if not isinstance(value, datetime):
            raise TypeError('a datetime is required')
        return int(value.timestamp())

    def _create_token(
            self,
            subject: Union[str, int],
            token_type: str,
            exp_time: Optional[int],
            user_claims: Dict,
            fresh: Optional[bool] = False,
    ) -> Token:
        """
        Create token for access_token and refresh_token (utf-8)
        :param subject: Identifier for who this token is for example id or username from database.
        :param token_type: indicate token is access_token or refresh_token
        :param exp_time: Set the duration of the JWT
        :param fresh: Optional when token is access_token this param required
        :param user_claims: Custom claims to include in this token. This data must be dictionary
        :return: Encoded token
        """
        # Validation type data
        if not isinstance(subject, (str, int)):
            raise TypeError("subject must be a string or integer")
        if not isinstance(fresh, bool):
            raise TypeError("fresh must be a boolean")
        if user_claims and not isinstance(user_claims, dict):
            raise TypeError("user_claims must be a dictionary")

        # Data section
        jti = self._create_jwt_identifier()
        reserved_claims = {
            "sub": subject,
            "iat": self._get_int_from_datetime(datetime.now(timezone.utc)),
            "nbf": self._get_int_from_datetime(datetime.now(timezone.utc)),
            "jti": jti
        }

        custom_claims = {"type": token_type}

        # for access_token only fresh needed
        if token_type == TokenTypeEnum.ACCESS_TOKEN:
            custom_claims['fresh'] = fresh

        if exp_time:
            reserved_claims['exp'] = exp_time

        try:
            secret_key = self._get_secret_key(token_type=token_type)
        except Exception:
            raise

        token = jwt.encode(
            {
                **reserved_claims,
                **custom_claims,
                **user_claims
            },
            secret_key,
            algorithm=self._algorithm,
        )

        return Token(token=token, token_type=token_type, jti=jti)

    @staticmethod
    def _get_secret_key(token_type: str):
        if token_type == TokenTypeEnum.ACCESS_TOKEN:
            return settings.access_token_secret_key
        elif token_type == TokenTypeEnum.REFRESH_TOKEN:
            return settings.refresh_token_secret_key
        raise TokenTypeInvalidError

    def _get_expired_time(self, token_type: str) -> Union[None, int]:
        """
        :param token_type: indicate token is access_token or refresh_token
        :return: duration exp claim jwt
        """

        if token_type == TokenTypeEnum.ACCESS_TOKEN:
            expires_time = self._access_token_expires
        elif token_type == TokenTypeEnum.REFRESH_TOKEN:
            expires_time = self._refresh_token_expires
        else:
            raise TokenTypeInvalidError
        return self._get_int_from_datetime(datetime.now(timezone.utc)) + expires_time

    def create_access_token(self, subject: Union[str, int], fresh: Optional[bool] = False,
                            user_claims: Optional[Dict] = None) -> Token:
        """
        Create a access token with 15 minutes for expired time (default),
        info for param and return check to function create token
        :return: hash token
        """
        user_claims = user_claims or {}
        return self._create_token(
            subject=subject,
            token_type=TokenTypeEnum.ACCESS_TOKEN,
            exp_time=self._get_expired_time("access"),
            fresh=fresh,
            user_claims=user_claims,
        )

    def create_refresh_token(self, subject: Union[str, int], user_claims: Optional[Dict] = None) -> Token:
        """
        Create a refresh token with 30 days for expired time,
        info for param and return check to function create token
        :return: hash token
        """
        user_claims = user_claims or {}
        return self._create_token(
            subject=subject,
            token_type=TokenTypeEnum.REFRESH_TOKEN,
            exp_time=self._get_expired_time("refresh"),
            user_claims=user_claims
        )

    def _parse_token(self, token: str, token_type: str):
        secret_key = self._get_secret_key(token_type=token_type)
        try:
            return jwt.decode(
                token,
                secret_key,
                algorithms=[self._algorithm]
            )
        except BaseException as ex:
            logging.info(ex)
            return None

    def parse_refresh_token(self, token):
        return self._parse_token(token=token, token_type=TokenTypeEnum.REFRESH_TOKEN)

    def parse_access_token(self, token):
        return self._parse_token(token=token, token_type=TokenTypeEnum.ACCESS_TOKEN)
