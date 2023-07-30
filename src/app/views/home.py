from fastapi import APIRouter

home_router = APIRouter(prefix=f'', tags=['home'])


@home_router.get("/health")
def health():
    return {"message": "Healthy!"}
