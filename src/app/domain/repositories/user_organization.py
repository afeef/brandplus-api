from abc import ABC, abstractmethod

from app.models import VersionedModel


class UserOrganizationRepository(ABC):
    @abstractmethod
    def get_user_organization_index(self):
        pass

    @abstractmethod
    def get_user_organization_entity_id_index(self):
        pass

    @abstractmethod
    def get_user_organization_user_id_index(self):
        pass

    @abstractmethod
    def get_user_organization_user_id_organization_id_index(self):
        pass

    @abstractmethod
    def get_user_organization_organization_id_index(self):
        pass

    @abstractmethod
    def is_user_organization_exists(self, o: VersionedModel):
        pass

    @abstractmethod
    def get_user_organization_by_user_id_organization_id(self, organization_id: str, user_id: str):
        pass

    @abstractmethod
    def get_all_user_organization_by_organization_id(self, organization_id: str):
        pass

    @abstractmethod
    def get_all_user_organization_by_user_id(self, user_id: str):
        pass

    @abstractmethod
    def get_user_organization_by_user_id(self, user_id: str):
        pass
