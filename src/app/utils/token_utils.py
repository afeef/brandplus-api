import logging
import time
from typing import Dict

import jwt
from itsdangerous import URLSafeTimedSerializer

from app.settings import settings


def generate_url_safe_token(email: str, app_secret_key: str, security_password_salt: str, token_expiry: int):
    serializer = URLSafeTimedSerializer(app_secret_key)
    current_ux_ts = time.time()
    expires_in = int(current_ux_ts) + token_expiry
    return serializer.dumps(email, salt=security_password_salt), expires_in


def parse_url_safe_token(token, app_secret_key: str, security_password_salt: str, token_expiry: int):
    serializer = URLSafeTimedSerializer(app_secret_key)
    try:
        email = serializer.loads(
            token,
            salt=security_password_salt,
            max_age=token_expiry
        )
    except BaseException as ex:
        logging.info(ex)
        return False
    return email


def generate_token(entity_id: str, token_secret_key: str, token_expiry: int):
    return jwt.encode(
        {
            'sub': entity_id,
            'exp': time.time() + token_expiry
        },
        token_secret_key,
        algorithm='HS256'
    )


def parse_token(token, token_secret_key: str):
    try:
        entity_id = jwt.decode(
            token,
            token_secret_key,
            algorithms=['HS256']
        )['sub']
        return entity_id
    except BaseException as ex:
        logging.info(ex)
        return


def generate_invitation_token(data: Dict, token_secret_key: str):
    return jwt.encode(
        data,
        token_secret_key,
        algorithm='HS256'
    )


def parse_invitation_token(token, token_secret_key: str):
    try:
        return jwt.decode(
            token,
            token_secret_key,
            algorithms=['HS256']
        )
    except BaseException as ex:
        logging.info(ex)
        return


def generate_confirmation_token(email):
    token, _ = generate_url_safe_token(
        email=email,
        app_secret_key=settings.secret_key,
        security_password_salt=settings.security_password_salt,
        token_expiry=settings.access_token_expire
    )
    return token


def parse_confirmation_token(token):
    # confirmation token expiry is set to be 7 days
    return parse_url_safe_token(
        token=token,
        app_secret_key=settings.secret_key,
        security_password_salt=settings.security_password_salt,
        token_expiry=86400 * 7
    )


def generate_reset_password_token(entity_id):
    token = generate_token(
        entity_id=entity_id,
        token_secret_key=settings.secret_key,
        token_expiry=settings.security_password_salt
    )
    return token


def parse_reset_password_token(token):
    return parse_token(
        token=token,
        token_secret_key=settings.secret_key,
    )
