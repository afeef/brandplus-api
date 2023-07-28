from enum import Enum

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


class Environment(Enum):
    development = 'development'
    test = 'test'
    production = 'production'


class MongoDBSettings(BaseSettings):
    host: str = Field(env='MONGO_HOST')
    port: str = Field(env='MONGO_PORT')
    user: str = Field(env='MONGODB_USER')
    password: str = Field(env='MONGODB_PASSWORD')
    database: str = Field(env='MONGODB_DATABASE')

    @property
    def database_url(self):
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    environment: Environment = Field(env='ENVIRONMENT')


class BrandPlusSettings(BaseSettings):
    db: MongoDBSettings = MongoDBSettings()


class ProductionSettings(BrandPlusSettings):
    pass


class DevelopmentSettings(BrandPlusSettings):
    pass


class TestSettings(BrandPlusSettings):
    pass


current_environment = Settings().environment

if current_environment == Environment.development:
    settings = DevelopmentSettings()
elif current_environment == Environment.test:
    settings = TestSettings()
elif current_environment == Environment.production:
    settings = ProductionSettings()
else:
    raise ValidationError("Invalid Environment")
