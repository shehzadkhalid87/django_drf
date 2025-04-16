# auth_app/models/user.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.enums.enums import ROLES, ACCOUNT_STATUS
from core.models.base import BaseModel
from core.models.timestamp import TimeStampModel


class UserEntityManager(BaseUserManager):
    """
    Custom User Entity Manager to handle custom fields and operations
    """

    def create_user(self, **extra_fields):
        """
        Create common user
        :params: UserEntity fields
        :return: user
        """
        email, password, role = (extra_fields.get("email"),
                                 extra_fields.get("password"),
                                 extra_fields.get("role"))
        extra_fields.pop("email")
        if not email or not password or not role:
            raise ValueError(_("The email and password must be set"))
        email = self.normalize_email(email=email.strip())
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **extra_fields):
        """
        Create and return a superuser.
        :params: user fields
        :return: user
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("google_email_verification", True)
        extra_fields.setdefault("role", ROLES.SUPER_ADMIN.value[0])  # Assign the Super Admin role

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(**extra_fields)


class UserEntity(AbstractBaseUser, PermissionsMixin, BaseModel, TimeStampModel):
    """
    Model: User model and profile
    """
    full_name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=128, choices=ROLES.choices())
    phone_number = models.CharField(max_length=15, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    google_email_verification = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    status = models.CharField(max_length=128, choices=ACCOUNT_STATUS.choices(),default=ACCOUNT_STATUS.COMPLETE.value[0])
    email_token_used = models.BooleanField(default=False)
    forgot_password_token_used = models.BooleanField(default=True)
    is_de_activated = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    objects = UserEntityManager()

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Metaclass to set db table name
        """
        db_table = "users"
