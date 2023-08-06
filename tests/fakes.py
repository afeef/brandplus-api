from uuid import uuid4

from pydantic import BaseModel, EmailStr

from app.settings import settings


def fake_email() -> str:
    return f'{settings.tests_prefix}_{str(uuid4())}@brandplus.app'


class FakeModel(BaseModel):
    pass


class FakeCredentials(FakeModel):
    email: EmailStr
    password: str


class FakeUser(FakeCredentials):
    pass


def fake_credentials() -> FakeCredentials:
    return FakeCredentials(
        email=fake_email(),
        password=settings.system_admin_default_password
    )


def fake_user() -> FakeUser:
    return FakeUser(
        email=fake_email(),
        password=settings.system_admin_default_password
    )
