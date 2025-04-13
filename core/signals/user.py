from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth_app.models.user import UserEntity
from auth_app.utils import AuthUtils
from core.enums.enums import ROLES


@receiver(post_save, sender=UserEntity)
def send_welcome_email_on_signup(sender, instance, created, **kwargs):
    """
    Signal to send verification email link.
    :param sender: The model class.
    :param instance: The actual instance being saved.
    :param created: A boolean; True if a new record was created.
    """
    if created and instance.role.lower() != ROLES.CANDIDATE.value[0].lower():
        # This code will only run if the user was created, not updated.
        # Send the email asynchronously
        # make sure send email when transaction is commited
        transaction.on_commit(lambda: AuthUtils.send_signup_verification_email(instance))
    elif created and instance.role.lower() == ROLES.CANDIDATE.value[0].lower():
        transaction.on_commit(lambda: AuthUtils.send_candidate_email_for_account_creation(instance))
