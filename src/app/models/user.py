import string
import time
from enum import StrEnum
from typing import List
from typing import Optional, Dict

from app.utils.auth_utils import AuthJWT
from passlib.context import CryptContext
from pydantic import Field, EmailStr, validator

from app.exceptions import PasswordValidationError
from app.models.versioned import VersionedModel

ALLOWED_SYMBOLS = '!@#$%&()-_[]{};:"./<>?^*`~\',|=+ '

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def has_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


class PasswordCharacterWhitelist:
    uppercase_letters: List = list(string.ascii_uppercase)
    lowercase_letters: List = list(string.ascii_lowercase)
    numbers: List = list(string.digits)
    symbols: List = list(ALLOWED_SYMBOLS)
    whitelist: List = uppercase_letters + lowercase_letters + numbers + symbols


class UserRoleEnum(StrEnum):
    SUPER_ADMIN = 'admin'
    BROKER = 'broker'
    CLIENT = 'client'

    @classmethod
    def values(cls):
        return list(map(lambda r: r.value, UserRoleEnum))

    @classmethod
    def get_list(cls):
        return [e for e in cls if e != cls.SUPER_ADMIN]


class User(VersionedModel):
    """User represents collection of users as an entity."""
    first_name: str = Field(example="Roronoa")
    last_name: str = Field(example="Zoro")
    role: UserRoleEnum
    verified: bool = Field(default=False, example=True)
    raw_password: Optional[str] = Field(example='Raw User password')
    subdomain: Optional[str] = Field(default=None, example='lockton')
    email: EmailStr = Field(example='test@ecorrogue.com')
    verified_on: int = Field(default=None)
    password_hash: Optional[str] = Field(default=None)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    refresh_token_jti: List[str] = Field(default=[], example=['ed80565cb78a4a648e5aac99b9a87f4d'])
    force_password_reset: Optional[bool] = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_hash = has_password(self.raw_password) if \
            self.raw_password else self.password_hash

    def __eq__(self, other) -> bool:
        if isinstance(other, User):
            return self.first_name == other.first_name and \
                self.last_name == other.last_name and \
                self.email == other.email and \
                self.password_hash == other.password_hash and \
                self.verified == other.verified and \
                self.verified_on == other.verified_on and \
                self.subdomain == other.subdomain
        else:
            return False

    def __str__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

    @validator("raw_password")
    def password_requirement_check(cls, v):
        if v is None:
            return v
        unique_v = set(v)
        if len(v) < 8:
            raise PasswordValidationError("Password must be at least 8 character long")
        if len(v) > 100:
            raise PasswordValidationError("Password must be at max 100 character long")
        if not any(map(lambda x: x in unique_v, PasswordCharacterWhitelist().uppercase_letters)):
            raise PasswordValidationError("Password must contain a uppercase letter")
        if not any(map(lambda x: x in unique_v, PasswordCharacterWhitelist().lowercase_letters)):
            raise PasswordValidationError("Password must contain a lowercase letter")
        if not any(map(lambda x: x in unique_v, PasswordCharacterWhitelist().numbers)):
            raise PasswordValidationError("Password must contain a digit")
        if not any(map(lambda x: x in unique_v, PasswordCharacterWhitelist().symbols)):
            raise PasswordValidationError("Password must contain a special character")
        if not all(map(lambda x: x in PasswordCharacterWhitelist().whitelist, unique_v)):
            raise PasswordValidationError("Password contains an invalid character")
        return v

    def get_for_db(self):
        keys_not_needed = ['raw_password']
        return {
            key: value for key, value in self.__dict__.items() if key not in keys_not_needed
        }

    def create_access_token(self, user_claims: Optional[Dict] = None, fresh: bool = True):
        user_claims = user_claims or {}
        token = AuthJWT().create_access_token(subject=self.email, fresh=fresh, user_claims=user_claims)
        self.access_token = token.token

    def create_refresh_token(self, user_claims: Optional[Dict] = None):
        user_claims = user_claims or {}
        token = AuthJWT().create_refresh_token(subject=self.email, user_claims=user_claims)
        self.refresh_token = token.token
        self.refresh_token_jti = self.refresh_token_jti + [token.jti]
        return token.jti

    def create_tokens(self):
        refresh_token_jti = self.create_refresh_token()
        self.create_access_token(user_claims={"rt_jti": refresh_token_jti})

    def as_detail(self):
        keys_to_include = [
            'first_name', 'last_name', 'email', 'entity_id', 'verified', 'role'
        ]
        return {
            key: value for key, value in self.__dict__.items() if key in keys_to_include
        }

    def confirm_email(self):
        self.verified = True
        self.verified_on = int(time.time())

    def confirm_password_change(self):
        self.force_password_reset = False

    def is_password_valid(self, raw_password) -> bool:
        return verify_password(password=raw_password, hashed_password=self.password_hash)
