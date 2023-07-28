from enum import Enum

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


class Environment(Enum):
    development = 'development'
    test = 'test'
    production = 'production'


class BrandPlusSettings(BaseSettings):
    environment: Environment = Field(env='ENVIRONMENT')


class Settings(BrandPlusSettings):

    sentry_dsn: str = Field(env='SENTRY_DSN')

    host: str = Field(env='MONGO_HOST')
    port: str = Field(env='MONGO_PORT')
    user: str = Field(env='MONGODB_USER')
    password: str = Field(env='MONGODB_PASSWORD')
    database: str = Field(env='MONGODB_DATABASE')

    @property
    def database_url(self):
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


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
