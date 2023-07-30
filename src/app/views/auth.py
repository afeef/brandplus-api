import time

from app.models import User, UserRoleEnum
from app.settings import settings
from app.utils.auth_utils import verify_password
from app.views.models import CreateUserSchema, LoginUserSchema
from fastapi import APIRouter, status, HTTPException, Depends

auth_router = APIRouter(prefix=f'/authentication', tags=["authentication"])


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUserSchema, repo=Depends(settings.get_repo)):
    user = repo.get_user_by_email(email=payload.email.lower())
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='Account already exist'
        )

    if payload.password != payload.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    user = User(
        email=payload.email.lower(),
        first_name=payload.first_name,
        last_name=payload.last_name,
        raw_password=payload.password,
        role=UserRoleEnum.CLIENT,
        verified_on=int(time.time()),
        force_password_reset=payload.verified
    )

    user.changed_by_id = user.entity_id
    user = repo.register_user(user=user)
    user = repo.login(user)

    response = dict(
        success=True,
        message="User successfully created and a confirmation email has been sent via email.",
        user=user
    )

    return response


@auth_router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(payload: LoginUserSchema, repo=Depends(settings.get_repo)):
    user = repo.get_user_by_email(email=payload.email.lower())

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password'
        )

    if not verify_password(password=payload.password, hashed_password=user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password'
        )

    user.changed_by_id = user.entity_id
    response = dict(success=True, message="Login successful!", user=repo.login(user))

    return response
