import os
from enum import Enum

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class Environment(Enum):
    development = 'development'
    test = 'test'
    production = 'production'


class PostgresSettings(BaseSettings):
    host: str = Field(env='POSTGRES_HOST')
    port: str = Field(env='POSTGRES_PORT')
    user: str = Field(env='POSTGRES_USER')
    password: str = Field(env='POSTGRES_PASSWORD')
    database: str = Field(env='POSTGRES_DATABASE')

    @property
    def database_url(self):
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_engine(self):
        assert self.database_url, 'Please set database environment variables correctly!'
        return create_engine(self.database_url)

    def get_session(self):
        assert self.database_url, 'Please set database environment variables correctly!'
        return scoped_session(sessionmaker(bind=create_engine(self.database_url)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir=os.environ.get('SECRETS_DIR'))

    environment: Environment = None


class BrandPlusSettings(BaseSettings):
    db: PostgresSettings = PostgresSettings()


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
