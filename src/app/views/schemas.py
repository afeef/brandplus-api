from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from pydantic.types import constr


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    password_confirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponseSchema(UserBaseSchema):
    id: str
    pass


class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema
