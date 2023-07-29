import re
import time
from typing import Optional, List

from app.domain import collection_names
from app.exceptions import AccessTokenInvalidError, RefreshTokenInvalidError
from app.domain.repositories import AuthenticationRepository
from app.models import UserRoleEnum, User
from app.utils.auth_utils import AuthJWT


class MongoDBAuthenticationRepository(AuthenticationRepository):

    def get_user_index(self):
        return f"__{collection_names.USER}_index__"

    def get_user_entity_id_index(self):
        return f"__{collection_names.USER}_entity_id_index__"

    def get_revoked_token_index(self, collection_name: str):
        return f"__{collection_names.REVOKED_TOKEN}_index__"

    def get_revoked_token_entity_id_index(self, collection_name: str):
        return f"__{collection_names.REVOKED_TOKEN}_entity_id_index__"

    def get_revoked_token_jti_index(self):
        return f"__{collection_names.REVOKED_TOKEN}_jti_index__"

    def get_user_email_index(self):
        return f"__{collection_names.USER}_email_index__"

    def get_user_role_index(self):
        return f"__{collection_names.USER}_role_index__"

    def get_user_by_role(self, role: UserRoleEnum) -> List[User]:
        data = self.get_all(
            query=dict(role=role),
            index=self.get_user_role_index(),
            collection_name=collection_names.USER
        )
        return [User(**each) for each in data]

    def get_user_by_id(self, uuid: str) -> Optional[User]:
        data = self.get_one(
            collection_name=collection_names.USER,
            query=dict(entity_id=uuid),
            index=self.get_user_entity_id_index()
        )
        return User(**data) if data else None

    def is_user_exists(self, user: User):
        raise NotImplementedError

    def is_user_verified(self, user: User):
        return bool(user and user.verified)

    def is_token_revoked(self, jti: str):
        return self.get_count(
            query=dict(jti=jti),
            index=self.get_revoked_token_jti_index(),
            collection_name=collection_names.REVOKED_TOKEN
        ) > 0

    def get_token_by_jti(self, jti: str):
        data = self.get_one(
            query=dict(jti=jti),
            index=self.get_revoked_token_jti_index(),
            collection_name=collection_names.REVOKED_TOKEN
        )
        return RevokedToken(**data) if data else None

    def get_user_by_email(self, email: str):
        # making email case-insensitive
        data = self.get_one(
            query=dict(email=re.compile('^' + re.escape(email) + '$', re.IGNORECASE)),
            index=self.get_user_email_index(),
            collection_name=collection_names.USER
        )
        return User(**data) if data else None

    def validate_refresh_token(self, refresh_token: str):
        data = AuthJWT().parse_refresh_token(token=refresh_token)

        if not data:
            raise RefreshTokenInvalidError

        if self.is_token_revoked(jti=data.get('jti')):
            raise RefreshTokenInvalidError

        return self.get_user_by_email(data.get('sub'))

    def validate_access_token(self, token: str):
        data = AuthJWT().parse_access_token(token=token)

        if not data:
            raise AccessTokenInvalidError

        if self.is_token_revoked(jti=data.get('jti')):
            raise AccessTokenInvalidError

        return self.get_user_by_email(data.get('sub'))

    def revoke_token(self, token: RevokedToken):
        self.create(token.get_for_db(), collection_name=collection_names.REVOKED_TOKEN)

    def login(self, user: User):
        user.create_tokens()
        user = self.update_user(user)
        if user.role == UserRoleEnum.SUPER_ADMIN:
            return user.get_for_api()
        elif user.role == UserRoleEnum.CLIENT:
            organization, user_organization = self.get_organization_for_user(user=user)
            if organization and user_organization:
                return {
                    **user.get_for_api(),
                    **dict(
                        organization_id=organization.entity_id,
                        organization_name=organization.name_of_insured,
                        client_role=user_organization.role
                    )
                }
            return user.get_for_api()
        elif user.role == UserRoleEnum.BROKER:
            organization, user_organization = self.get_brokerage_for_user(user=user)
            if organization and user_organization:
                return {
                    **user.get_for_api(),
                    **dict(
                        brokerage_id=organization.entity_id,
                        brokerage_name=organization.name,
                        broker_role=user_organization.role
                    )
                }
            return user.get_for_api()
        else:
            raise Exception('User role is not known')

    def refresh(self, user: User, refresh_token: Optional[str] = None):
        if not refresh_token:
            refresh_token = g.refresh_token

        data = AuthJWT().parse_refresh_token(token=refresh_token)

        if not data:
            raise RefreshTokenInvalidError

        user.create_access_token(user_claims={"rt_jti": data.get('jti')}, fresh=False)

        user.refresh_token = refresh_token

        return self.update_user(user)

    def logout_user(self, user: User):
        data = AuthJWT().parse_access_token(token=g.access_token)
        if not data:
            return

        access_token_jti = data.get('jti')
        refresh_token_jti = data.get('rt_jti')

        revoked_tokens = [
            RevokedToken(
                jti=access_token_jti,
                token_type=TokenTypeEnum.ACCESS_TOKEN,
                user_email=data.get('sub'),
                created_at=int(time.time())
            ),
            RevokedToken(
                jti=refresh_token_jti,
                token_type=TokenTypeEnum.REFRESH_TOKEN,
                user_email=data.get('sub'),
                created_at=int(time.time())
            )
        ]
        for token in revoked_tokens:
            self.revoke_token(token)
        try:
            user.refresh_token_jti.remove(refresh_token_jti)
            self.update_user(user)
        except ValueError:
            pass

    def revoke_all_refresh_tokens(self, user: User):
        for refresh_jti in user.refresh_token_jti:
            revoked_token = RevokedToken(
                jti=refresh_jti,
                token_type=TokenTypeEnum.REFRESH_TOKEN,
                user_email=user.email,
                created_at=int(time.time())
            )
            self.revoke_token(revoked_token)
        user.refresh_token_jti = []
        return self.update_user(user)

    def register_user(self, user: User) -> User:
        self.create_user(user)
        self.send_confirmation_link(user)
        return user

    def send_confirmation_link(self, user: User):
        if user.verified is False:
            send_verification_email(user.get_for_api())

    def send_reset_password_email(self, user: User):
        send_password_reset_email(user.get_for_api())

    def confirm_user_email(self, user: User):
        user.confirm_email()
        return self.update_user(user)

    def create_user(self, user: User):
        self.create(data=user.get_for_db(), collection_name=collection_names.USER)

    def update_user(self, user: User):
        user = self.update(data=user.get_for_db(), collection_name=collection_names.USER)
        return User(**user)

    def delete_user(self, user: User):
        self.delete(data=user.get_for_db(), collection_name=collection_names.USER)
