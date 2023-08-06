from uuid import uuid4

from faker import Faker
from pydantic import BaseModel, EmailStr

from app.settings import settings

fake = Faker()


def fake_email() -> str:
    return f'{settings.tests_prefix}_{uuid4().hex}@brandplus.app'


class FakeModel(BaseModel):
    pass


class FakeCredentials(FakeModel):
    email: EmailStr
    password: str


class FakeUser(FakeCredentials):
    first_name: str
    last_name: str
    verified: bool
    password_confirm: str


def fake_credentials() -> FakeCredentials:
    return FakeCredentials(
        email=fake_email(),
        password=settings.system_admin_default_password
    )


def fake_user() -> FakeUser:
    return FakeUser(
        email=fake_email(),
        password=settings.system_admin_default_password,
        password_confirm=settings.system_admin_default_password,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        verified=False
    )
