import sentry_sdk
from app.views import home_router, auth_router
from fastapi import FastAPI

from app.settings import settings

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0
)
app = FastAPI(title='BrandPlus API')

home_router.include_router(auth_router)

app.include_router(home_router)
