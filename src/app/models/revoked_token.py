from pydantic import Field, EmailStr

from app.models import VersionedModel
from app.utils.auth_utils import TokenTypeEnum


class RevokedToken(VersionedModel):
    jti: str = Field(example="00001010200101203040501230403823")
    token_type: TokenTypeEnum
    user_email: EmailStr = Field(example='test@ecorrogue.com')
    created_at: int

    def _new_from_existing(self):
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, RevokedToken):
            return self.jti == other.jti and self.token_type == other.token_type and self.user_email == other.user_email
        return False

    def __str__(self):
        return '<TokenBlockList {} of user {}>'.format(self.token_type, self.user_email)
