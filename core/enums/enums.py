# enums/enums
import enum

from django.utils.translation import gettext_lazy as _


class GENDER(enum.Enum):
    """
    Enumeration for representing user genders.

    Attributes:
        MALE: Represents male gender.
        FEMALE: Represents female gender.
        OTHER: Represents other gender.

    Methods:
        choices: Returns a list of tuples containing the
        gender values and their corresponding labels.
    """
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the gender values and their corresponding labels.

        :return: List of tuples [(value, label), ...]
        """
        return [(tag.value[0], tag.value[1]) for tag in cls]


class ROLES(enum.Enum):
    """
    Enumeration for representing user roles in the system.

    Attributes:
        SUPER_ADMIN: Represents a super admin role.
        EDUCATOR: Represents an Educator user role.
        COMPANY: Represents a company user role.
        CANDIDATE: Represents a candidate user role.

    Methods:
        choices: Returns a list of tuples containing the role values and their corresponding labels.
    """
    SUPER_ADMIN = "super_admin", _("Super Admin")
    EDUCATOR = "educator", _("Educator")
    COMPANY = "company", _("Company")
    CANDIDATE = "candidate", _("Candidate")

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the role
        values and their corresponding labels.

        :return: List of tuples [(value, label), ...]
        """
        return [(tag.value[0], tag.value[1]) for tag in cls]


class USER_UPDATE_ACTIONS(enum.Enum):
    """
    Enumeration for user update actions.

    Attributes:
        BLOCK: Represents the action to block a user.
        UNBLOCK: Represents the action to unblock a user.
        ACTIVATE: Represents the action to activate a user.
        DEACTIVATE: Represents the action to deactivate a user.

    Methods:
        choices: Returns a list of possible actions.
        send_values: Returns a list of tuples containing
        the action values and their corresponding names.
    """
    BLOCK = "block"
    UNBLOCK = "unblock"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"

    @classmethod
    def choices(cls):
        """
        Returns a list of possible user update actions.

        :return: List of user update actions.
        """
        return [tag for tag in cls]

    @classmethod
    def send_values(cls):
        """
        Returns a list of tuples containing the action values and their corresponding names.

        :return: List of tuples [(value, name), ...]
        """
        return [(tag.value, tag.name) for tag in cls]


class ACCOUNT_STATUS(enum.Enum):
    """
    Enumeration for representing account statuses.

    Attributes:
        PENDING: Represents a pending account status.
        COMPLETE: Represents a complete account status.

    Methods:
        choices: Returns a list of tuples containing the
        account status values and their corresponding labels.
    """
    PENDING = "pending", _("Pending")
    COMPLETE = "complete", _("Complete")

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the account
        status values and their corresponding labels.

        :return: List of tuples [(value, label), ...]
        """
        return [(tag.value[0], tag.value[1]) for tag in cls]


class SUBSCRIPTION_STATUS(enum.Enum):
    """
    Enumeration for representing subscription statuses.

    Attributes:
        PAID: Represents a paid subscription status.
        PENDING: Represents a pending subscription status.
        UNPAID: Represents an unpaid subscription status.
        CANCELED: Represents a canceled subscription status.
        CREATED: Represents a created subscription status.

    Methods:
        choices: Returns a list of tuples containing the
        subscription status values and their corresponding labels.
    """
    PAID = "paid", _("Paid")
    PENDING = "pending", _("Pending")
    UNPAID = "unpaid", _("Unpaid")
    CANCELED = "canceled", _("Canceled")
    CREATED = "created", _("Created")

    @classmethod
    def choices(cls):
        """
        Returns a list of tuples containing the subscription
        status values and their corresponding labels.

        :return: List of tuples [(value, label), ...]
        """
        return [(tag.value[0], tag.value[1]) for tag in cls]
