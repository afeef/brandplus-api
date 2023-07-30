from enum import Enum
from typing import List

from pydantic import ValidationError
from pydantic_settings import BaseSettings


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

    secret_key: str
    security_password_salt: str
    access_token_expire: int
    refresh_token_expire: int
    access_token_secret_key: str
    refresh_token_secret_key: str
    frontend_url: str

    broker_path: str = None
    rabbitmq_vhost: str = None
    rabbitmq_user: str = None
    rabbitmq_password: str = None

    system_admin_email_list: str
    system_admin_default_password: str

    @property
    def database_url(self):
        return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongo_host}:{self.mongo_port}/{self.mongodb_database}"

    def get_repo(self):
        from app.domain.mongodb.repository import MongoDBRepository
        return MongoDBRepository(mongo_uri=self.database_url, mongo_database=self.mongodb_database)


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
