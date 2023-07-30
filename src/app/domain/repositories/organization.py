from abc import ABC, abstractmethod

from app.models import VersionedModel
from app.models import Organization
from app.models.user import User


class OrganizationRepository(ABC):
    @abstractmethod
    def get_organization_index(self):
        pass

    @abstractmethod
    def get_organization_name_index(self):
        pass

    @abstractmethod
    def get_organization_entity_id_index(self):
        pass

    @abstractmethod
    def get_organization_by_id(self, uuid: str) -> Organization:
        pass

    @abstractmethod
    def is_organization_exists(self, o: VersionedModel):
        pass

    @abstractmethod
    def get_organization_by_name(self, organization_name: str):
        pass

    @abstractmethod
    def get_organization_user_role(self, user_id: str, organization_id: str):
        pass

    @abstractmethod
    def create_organization(self, organization: Organization, user: User):
        pass

    @abstractmethod
    def delete_organization(self, organization):
        pass

    @abstractmethod
    def get_users_in_organization(self, organization_id: str):
        pass

    @abstractmethod
    def get_organizations_for_user(self, user: User):
        pass

    @abstractmethod
    def get_organization_for_user(self, user: User):
        pass

    @abstractmethod
    def is_user_part_of_organization(self, organization_name, user: User):
        pass

    @abstractmethod
    def get_all_organizations(self):
        pass

    @abstractmethod
    def update_organization(self, organization: Organization):
        pass
