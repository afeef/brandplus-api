from enum import Enum

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(Enum):
    development = 'development'
    test = 'test'
    production = 'production'


class BrandPlusSettings(BaseSettings):
    environment: Environment


class Settings(BrandPlusSettings):
    sentry_dsn: str

    mongo_host: str
    mongo_port: str
    mongodb_user: str
    mongodb_password: str
    mongodb_database: str

    access_token_expire: int
    refresh_token_expire: int
    access_token_secret_key: str
    refresh_token_secret_key: str

    @property
    def database_url(self):
        return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongo_host}:{self.mongo_port}/{self.mongodb_database}"


class ProductionSettings(Settings):
    pass


class DevelopmentSettings(Settings):
    pass


class TestSettings(Settings):
    pass


current_environment = BrandPlusSettings().environment

if current_environment == Environment.development:
    settings = DevelopmentSettings()
elif current_environment == Environment.test:
    settings = TestSettings()
elif current_environment == Environment.production:
    settings = ProductionSettings()
else:
    raise ValidationError("Invalid Environment")
