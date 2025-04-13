from dataclasses import dataclass
from auth_app.models import UserEntity
from core.base import BaseResult


@dataclass(frozen=True)
class RefreshTokenResult(BaseResult):
    refresh_token: str
    access_token: str

@dataclass(frozen=True)
class LoginResult(RefreshTokenResult):
    user: UserEntity
