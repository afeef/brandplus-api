from app.domain import collection_names
from app.domain.repositories import OrganizationRepository
from app.models import VersionedModel, User, UserRoleEnum, Organization, UserOrganization


class MongoDBOrganizationRepository(OrganizationRepository):

    def get_organization_index(self):
        return f"__{collection_names.ORGANIZATION}_index__"

    def get_organization_name_index(self):
        return f"__{collection_names.ORGANIZATION}_name_index__"

    def get_organization_entity_id_index(self):
        return f"__{collection_names.ORGANIZATION}_entity_id_index__"

    def get_organization_by_id(self, uuid: str) -> Organization:
        data = self.get_one(
            collection_name=collection_names.ORGANIZATION,
            query=dict(entity_id=uuid),
            index=self.get_organization_entity_id_index()
        )
        return Organization(**data) if data else None

    def is_organization_exists(self, o: VersionedModel):
        return NotImplementedError

    def get_organization_by_name(self, organization_name: str):
        data = self.get_one(
            query=dict(name_of_insured=organization_name),
            index=self.get_organization_name_index(),
            collection_name=collection_names.ORGANIZATION
        )
        return Organization(**data) if data else None

    def get_organization_user_role(self, user_id: str, organization_id: str):
        return self.get_user_organization_by_user_id_organization_id(
            user_id=user_id,
            organization_id=organization_id
        )

    def create_organization(self, organization: Organization, user: User):
        self.create(organization.get_for_db(), collection_name=collection_names.ORGANIZATION)
        user_organization = UserOrganization(
            organization_id=organization.entity_id, user_id=user.entity_id, role='admin'
        )
        self.create(user_organization.get_for_db(), collection_name=collection_names.USER_ORGANIZATION)

    def delete_organization(self, organization):
        self.delete(organization.get_for_db(), collection_name=collection_names.ORGANIZATION)

        user_organizations = self.get_all_user_organization_by_organization_id(
            organization_id=organization.entity_id
        )
        for user_org in user_organizations:
            self.delete(user_org.get_for_db(), collection_name=collection_names.USER_ORGANIZATION)

        cyber_security = self.get_cyber_security_in_organization(organization_id=organization.entity_id)
        if cyber_security:
            self.delete(cyber_security.get_for_db(), collection_name=collection_names.CYBER_SECURITY)

        questionnaire = self.get_questionnaire_in_organization(organization_id=organization.entity_id)
        if questionnaire:
            self.delete(questionnaire.get_for_db(), collection_name=collection_names.QUESTIONNAIRE)

        cyber_pre_check = self.get_cyber_precheck_in_organization(organization_id=organization.entity_id)
        if cyber_pre_check:
            self.delete(cyber_pre_check.get_for_db(), collection_name=collection_names.CYBER_PRECHECK)

    def get_users_in_organization(self, organization_id: str):
        return self.get_all_user_organization_by_organization_id(
            organization_id=organization_id
        )

    def delete_cyber_security_in_organization(self, organization_id: str):
        cyber_security = self.get_cyber_security_in_organization(organization_id=organization_id)
        if cyber_security:
            self.delete(cyber_security.get_for_db(), collection_name=collection_names.CYBER_SECURITY)

    def get_organizations_for_user(self, user: User):
        if user.role == UserRoleEnum.SUPER_ADMIN:
            return self.get_all_organizations()
        user_organization = self.get_all_user_organization_by_user_id(user_id=user.entity_id)
        data = self.get_all(
            collection_name=collection_names.ORGANIZATION,
            index=self.get_organization_entity_id_index(),
            query=dict(entity_id={'$in': [user_org.organization_id for user_org in user_organization]})
        )
        return [Organization(**each) for each in data]

    def get_organization_for_user(self, user: User):
        user_organization = self.get_user_organization_by_user_id(user_id=user.entity_id)
        if user_organization:
            organization = self.get_organization_by_id(
                uuid=user_organization.organization_id
            )
            return organization, user_organization
        return None, None

    def is_user_part_of_organization(self, organization_name, user: User):
        user_organization = self.get_all_user_organization_by_user_id(user_id=user.entity_id)
        organization = self.get_organization_by_name(organization_name=organization_name)
        return organization and organization.entity_id in [user_org.organization_id for user_org in user_organization]

    def get_all_organizations(self):
        data = self.get_all(
            index=self.get_organization_index(),
            collection_name=collection_names.ORGANIZATION
        )
        return [Organization(**each) for each in data]

    def update_organization(self, organization: Organization) -> Organization:
        organization = self.update(organization.get_for_db(), collection_name=collection_names.ORGANIZATION)
        return Organization(**organization)
