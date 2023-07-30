import time

from app.models import User, UserRoleEnum
from app.settings import settings
from app.views import schemas
from fastapi import APIRouter, Request, status, HTTPException, Depends

auth_router = APIRouter(prefix=f'/authentication', tags=["authentication"])


@auth_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(payload: schemas.CreateUserSchema, repo=Depends(settings.get_repo)):
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

    response = dict(
        success=True,
        message="User successfully created and a confirmation email has been sent via email.",
        user=repo.login(user)
    )

    return response
