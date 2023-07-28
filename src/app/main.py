import sentry_sdk
from fastapi import FastAPI

from app.settings import settings

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0
)
app = FastAPI(title='BrandPlus API')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/db")
async def db():
    assert settings.db.database_url
    return {"message": "database connected"}
