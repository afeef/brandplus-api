from app import deps
from app.logger import logger
from app.models.user import User
from app.settings import settings
from fastapi import APIRouter, Request, Depends

home_router = APIRouter(prefix=f'', tags=['home'])


@home_router.get("/health")
def health(request: Request, user: User = Depends(deps.get_current_user)):
    logger.info(user.__dict__)
    return {"message": "Healthy!"}


@home_router.get("/")
async def db(repo=Depends(settings.get_repo)):
    assert repo
    return {"message": "database connected"}
