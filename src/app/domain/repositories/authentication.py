from abc import ABC, abstractmethod
from typing import Optional, List

from app.models import User, UserRoleEnum, RevokedToken


class AuthenticationRepository(ABC):

    @abstractmethod
    def get_user_index(self):
        pass

    @abstractmethod
    def get_user_entity_id_index(self):
        pass

    @abstractmethod
    def get_user_email_index(self):
        pass

    @abstractmethod
    def get_user_role_index(self):
        pass

    @abstractmethod
    def get_revoked_token_index(self, collection_name: str):
        pass

    @abstractmethod
    def get_revoked_token_entity_id_index(self, collection_name: str):
        pass

    @abstractmethod
    def get_revoked_token_jti_index(self):
        pass

    @abstractmethod
    def get_user_by_role(self, role: UserRoleEnum) -> List[User]:
        pass

    @abstractmethod
    def get_user_by_id(self, uuid: str) -> User:
        pass

    @abstractmethod
    def is_user_exists(self, user: User):
        pass

    @abstractmethod
    def is_user_verified(self, user: User):
        pass

    @abstractmethod
    def is_token_revoked(self, jti: str):
        pass

    @abstractmethod
    def get_token_by_jti(self, jti: str):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        pass

    @abstractmethod
    def validate_refresh_token(self, refresh_token: str):
        pass

    @abstractmethod
    def validate_access_token(self, token: str):
        pass

    @abstractmethod
    def revoke_token(self, token: RevokedToken):
        pass

    @abstractmethod
    def login(self, user: User):
        pass

    @abstractmethod
    def refresh(self, user: User, refresh_token: Optional[str] = None):
        pass

    # @abstractmethod
    # def logout_user(self, user: User):
    #     pass

    @abstractmethod
    def register_user(self, user: User) -> User:
        pass

    @abstractmethod
    def send_confirmation_link(self, user: User):
        pass

    @abstractmethod
    def send_reset_password_email(self, user: User):
        pass

    @abstractmethod
    def confirm_user_email(self, user: User):
        pass

    @abstractmethod
    def create_user(self, user: User):
        pass

    @abstractmethod
    def update_user(self, user: User):
        pass

    @abstractmethod
    def delete_user(self, user: User):
        pass

    @abstractmethod
    def revoke_all_refresh_tokens(self, user: User) -> User:
        pass
