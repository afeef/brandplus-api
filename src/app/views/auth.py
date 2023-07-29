from app.views import schemas
from fastapi import APIRouter, Request, status

auth_router = APIRouter(prefix=f'/authentication', tags=["authentication"])


@auth_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(payload: schemas.CreateUserSchema):
    pass
