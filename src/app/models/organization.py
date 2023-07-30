from typing import Any

from pydantic import Field, Extra

from app.models import VersionedModel


class Organization(VersionedModel, extra=Extra.allow):
    name: str = Field(example="Acme, Inc.")
    contact_email: Any = Field(example='test@brandplus.com', default=None)
    address: Any = Field(example='123 Main Street', default=None)
    city: Any = Field(example='New York', default=None)
    state: Any = Field(example='NY', default=None)
    zipcode: Any = Field(example='10001', default=None)
    websites: Any = []

    def __eq__(self, other):
        if isinstance(other, Organization):
            return self.entity_id == other.entity_id
        return False

    def __str__(self):
        return f'<Organization {self.name}>'
