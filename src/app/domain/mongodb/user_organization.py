from app.domain import collection_names
from app.domain.repositories import UserOrganizationRepository
from app.models import VersionedModel, UserOrganization


class MongoDBUserOrganizationRepository(UserOrganizationRepository):

    def get_user_organization_index(self):
        return f"__{collection_names.USER_ORGANIZATION}_index__"

    def get_user_organization_entity_id_index(self):
        return f"__{collection_names.USER_ORGANIZATION}_entity_id_index__"

    def get_user_organization_user_id_index(self):
        return f"__{collection_names.USER_ORGANIZATION}_user_id_index__"

    def get_user_organization_user_id_organization_id_index(self):
        return f"__{collection_names.USER_ORGANIZATION}_user_id_organization_id_index__"

    def get_user_organization_organization_id_index(self):
        return f"__{collection_names.USER_ORGANIZATION}_organization_id_index__"

    def is_user_organization_exists(self, o: VersionedModel):
        return NotImplementedError

    def get_user_organization_by_user_id_organization_id(self, organization_id: str, user_id: str):
        data = self.get_one(
            query=dict(user_id=user_id, organization_id=organization_id),
            index=self.get_user_organization_user_id_organization_id_index(),
            collection_name=collection_names.USER_ORGANIZATION
        )
        return UserOrganization(**data) if data else None

    def get_all_user_organization_by_organization_id(self, organization_id: str):
        data = self.get_all(
            query=dict(organization_id=organization_id),
            index=self.get_user_organization_organization_id_index(),
            collection_name=collection_names.USER_ORGANIZATION
        )
        return [UserOrganization(**each) for each in data]

    def get_all_user_organization_by_user_id(self, user_id: str):
        data = self.get_all(
            query=dict(user_id=user_id),
            index=self.get_user_organization_user_id_index(),
            collection_name=collection_names.USER_ORGANIZATION
        )
        return [UserOrganization(**each) for each in data]

    def get_user_organization_by_user_id(self, user_id: str):
        data = self.get_one(
            query=dict(user_id=user_id),
            index=self.get_user_organization_user_id_index(),
            collection_name=collection_names.USER_ORGANIZATION
        )
        return UserOrganization(**data) if data else None
