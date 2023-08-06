import time

from pydantic import EmailStr

from app.deps import get_current_user_from_refresh_token, get_current_user
from app.models import User, UserRoleEnum
from app.settings import settings
from app.utils.auth_utils import verify_password
from app.utils.token_utils import parse_confirmation_token, generate_reset_password_token, parse_reset_password_token
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


@auth_router.post('/verify_email/{token}')
async def verify_email(token: EmailStr, repo=Depends(settings.get_repo)):
    email = parse_confirmation_token(token=token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Confirmation token has expired or is invalid'
        )

    user = repo.get_user_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User with email not found.'
        )

    if user.verified and user.force_password_reset is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User email already verified'
        )

    user.changed_by_id = user.entity_id

    if user.verified is False:
        repo.confirm_user_email(user)

    reset_token = generate_reset_password_token(user.email)

    response = dict(success=True, message='Email verified successfully!', reset_token=reset_token)
    return response


@auth_router.post('/resend_email_verification')
async def resend_email_verification(email: EmailStr, repo=Depends(settings.get_repo)):
    user = repo.get_user_by_email(email=email)

    if repo.is_user_verified(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User email already verified'
        )

    repo.send_confirmation_link(user=user)

    response = dict(success=True, message='Confirmation email resent successfully!')
    return response


@auth_router.post('/refresh_token')
async def refresh_token(
        email: EmailStr, user=Depends(get_current_user_from_refresh_token),
        repo=Depends(settings.get_repo)
):
    user = repo.get_user_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User with email not found.'
        )

    return dict(success=True, user=user.get_for_api())


@auth_router.post('/logout')
async def logout(user=Depends(get_current_user), repo=Depends(settings.get_repo)):
    repo.logout_user(user)

    response = dict(success=True, message='User successfully logged out.')
    return response


@auth_router.post('/forgot_password')
async def forgot_password(email: EmailStr, repo=Depends(settings.get_repo)):
    user = repo.get_user_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User with email not found.'
        )

    repo.send_reset_password_email(user=user)

    response = dict(success=True, message='Password reset email sent successfully!')
    return response


@auth_router.post('/reset_password/{token}')
async def reset_password(token: str, password: str, repo=Depends(settings.get_repo)):
    email = parse_reset_password_token(token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Reset password token has expired or is invalid.'
        )

    user = repo.get_user_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User with email not found.'
        )

    user.raw_password = password
    user = User(**user.dict())
    user.changed_by_id = user.entity_id
    user.confirm_password_change()

    updated_user = repo.revoke_all_refresh_tokens(user)

    response = dict(success=True, message='Password updated successfully!', user=repo.login(updated_user))
    return response
