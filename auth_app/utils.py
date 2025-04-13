from decouple import config

from auth_app.models import UserEntity
from core.utils.helper import generate_token, generate_uid
from pkg.services.email_service import EmailServicefrom decouple import config

from auth_app.models import UserEntity
from core.utils.helper import generate_token, generate_uid
from pkg.services.email_service import EmailService


class AuthUtils:
    """
    Utility class for Auth App
    """

    @staticmethod
    def send_welcome_email(email: str):
        """
        intermediate method to call EmailService
        """
        EmailService.send_welcome_email([email])

    @staticmethod
    def send_signup_verification_email(instance: UserEntity):
        """
        Send Email for verification
        :param instance of user
        """
        token = generate_token(instance)
        uid = generate_uid(instance.pk)
        # Build verification link
        verification_link = f"{config('FRONTEND_URL')}/account/verify/email/?uid={uid}&token={token}"
        recipient_list = [instance.email]  # Get the user's email from the instance
        EmailService.send_verification_email(recipient_list, verification_link)

    @staticmethod
    def send_forgot_password_email(instance: UserEntity):
        """
        Send Email for forgot password
        :param instance: UserEntity
        """

        token = generate_token(instance)
        uid = generate_uid(instance.pk)

        verification_link = f"{config('FRONTEND_URL')}/account/reset/password/?uid={uid}&token={token}"
        recipient_list = [instance.email]  # Get the user's email from the instance
        EmailService.send_forgot_password_email(recipient_list, verification_link)

    @staticmethod
    def send_candidate_email_for_account_creation(instance: UserEntity):
        """
        Send Email for complete account process for candidate
        :param instance of user
        """
        token = generate_token(instance)
        uid = generate_uid(instance.pk)
        # Build verification link
        verification_link = f"{config('FRONTEND_URL')}/account/complete/?uid={uid}&token={token}"
        recipient_list = [instance.email]  # Get the user's email from the instance
        EmailService.send_candidate_account_create_email(recipient_list, verification_link)
