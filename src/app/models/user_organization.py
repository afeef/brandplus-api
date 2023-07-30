from pydantic import Field

from app.models import VersionedModel


class UserOrganization(VersionedModel):
    organization_id: str = Field(example="00000000000000000000000000000000")
    user_id: str = Field(example="00000000000000000000000000000000")
    role: str = Field(example="admin")

    def __eq__(self, other):
        if isinstance(other, UserOrganization):
            return self.organization_id == other.organization_id and \
                   self.user_id == other.user_id and \
                   self.role == other.role
        return False

    def __str__(self):
        return f'<UserOrganization: {self.organization_id} -> {self.user_id}: {self.role}>'
