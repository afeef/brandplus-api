import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.exceptions import ClassInstanceMissmatchError


def get_uuid4_hex():
    return uuid.uuid4().hex


class VersionedModel(BaseModel):
    entity_id: str = Field(default_factory=get_uuid4_hex)
    version: str = Field(default_factory=get_uuid4_hex)
    previous_version: str = Field(default="00000000000000000000000000000000")
    active: bool = True
    latest: bool = True
    changed_by_id: Optional[str] = None
    changed_on: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @validator('changed_on', pre=True, always=True)
    def set_changed_on(cls, v):
        return v or datetime.utcnow().isoformat()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.changed_on = self.changed_on or datetime.utcnow().isoformat()
        self.changed_by_id = self.changed_by_id

    def update_version(self):
        self.previous_version = self.version
        self.version = uuid.uuid4().hex
        self.changed_on = datetime.utcnow().isoformat()

    def __eq__(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def dict(self, *args):
        return super().dict(exclude={'_id'})

    def as_dict(self):
        return self.dict()

    def get_for_api(self):
        keys_to_exclude = ['password_hash', 'raw_password', 'refresh_token_jti']
        return {
            key: value for key, value in self.dict().items() if key not in keys_to_exclude
        }

    def get_for_db(self):
        return {
            key: value for key, value in self.dict().items()
        }

    def set_from_other(self, model):
        for k, v in model.__dict__.items():
            setattr(self, k, v)

    def update_from(self, other):
        if not isinstance(other, self.__class__):
            raise ClassInstanceMissmatchError
        if other.entity_id:
            self.entity_id = other.entity_id
        if other.version:
            self.version = other.version

    def update_from_previous_version(self, other):
        if not isinstance(other, self.__class__):
            raise ClassInstanceMissmatchError
        if not other.entity_id == self.entity_id:
            raise ClassInstanceMissmatchError
        if other.previous_version:
            self.previous_version = other.version
        if other.changed_by_id:
            self.changed_by_id = other.changed_by_id

    def _new_from_existing(self):
        data = self.get_for_db()
        data['previous_version'] = data['version']
        data['version'] = get_uuid4_hex()
        return self.__class__(**data)
