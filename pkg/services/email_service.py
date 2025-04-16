import threading

from decouple import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import strip_tags

from auth_app.models import UserEntity


class EmailService:
    """
    A service class for handling email-related operations asynchronously.
    """

    @staticmethod
    def send_email_async(subject: str, message: str, recipient_list: list):
        """
        Sends an email asynchronously in a separate thread.

        :param subject: The subject of the email.
        :param message: The body of the email.
        :param recipient_list: A list of recipients to whom the email will be sent.
        """
        email_thread = threading.Thread(
            target=EmailService._send_email,
            args=(subject, message, recipient_list)
        )
        email_thread.start()

    @staticmethod
    def _send_email(subject: str, message: str, recipient_list: list):
        """
        The method that actually sends the email. It is run on a separate thread.

        :param subject: The subject of the email.
        :param message: The body of the email.
        :param recipient_list: A list of recipients to whom the email will be sent.
        """
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

    @staticmethod
    def send_welcome_email(recipient_list: list):
        """
        Example of an additional method for sending a welcome email.
        """
        subject = "Title message"
        # Create HTML content inline
        html_content = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Welcome Message</title>
                    </head>
                    <body>
                        <h2>Welcome to Our Platform!</h2>                        
                        <p>Thankyou for choosing platform_name, Please use the link to sign in the app.</p>
                        <br />
                        <p>If you did not sign up for this account, please ignore this email.</p>
                        <br>
                        <p>Best regards,</p>
                        <p>Your Company Team</p>
                    </body>
                    </html>
                    """
        # Convert HTML to plain text for fallback
        text_content = strip_tags(html_content)

        # Create the email object
        email = EmailMultiAlternatives(subject, text_content, from_email=config("FROM_EMAIL"), to=recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Send email in a separate thread to avoid blocking the request
        threading.Thread(target=email.send).start()

    @staticmethod
    def send_verification_email(recipient_list, verification_link):
        """
        Sends a verification email with a unique verification link.
        :param recipient_list: List of recipients (emails).
        :param verification_link: The URL for email verification.
        """

        subject = "Verify your email address"
        # Create HTML content inline
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Email Verification</title>
            </head>
            <body>
                <h2>Welcome to Our Platform!</h2>
                <p>Please click the link below to verify your email address:</p>
                <a href="{verification_link}" target="_blank">Verify your email</a>
                <p>If you did not sign up for this account, please ignore this email.</p>
                <br>
                <p>Best regards,</p>
                <p>Your Company Team</p>
            </body>
            </html>
            """
        # Convert HTML to plain text for fallback
        text_content = strip_tags(html_content)

        # Create the email object
        email = EmailMultiAlternatives(subject, text_content, from_email=config("FROM_EMAIL"), to=recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Send email in a separate thread to avoid blocking the request
        threading.Thread(target=email.send).start()

    @staticmethod
    def send_forgot_password_email(recipient_list, verification_link):
        """
        Sends a verification email with a unique verification link.
        :param recipient_list: List of recipients (emails).
        :param verification_link: The URL for email verification.
        """

        subject = "Forgot Password"
        # Create HTML content inline
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Forgot Password</title>
                </head>
                <body>
                    <h2>Forgot password was requested.</h2>
                    <p>Please click the link below to reset your password:</p>
                    <a href="{verification_link}" target="_blank">Reset password</a>
                    <p>If you did not sign up for this account, please ignore this email.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>Your Company Team</p>
                </body>
                </html>
                """
        # Convert HTML to plain text for fallback
        text_content = strip_tags(html_content)

        # Create the email object
        email = EmailMultiAlternatives(subject, text_content, from_email=config("FROM_EMAIL"), to=recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Send email in a separate thread to avoid blocking the request
        threading.Thread(target=email.send).start()

    @staticmethod
    def send_candidate_account_create_email(recipient_list, verification_link):
        """
        Sends a Candidate email to complete the account process.
        :param recipient_list: List of recipients (emails).
        :param verification_link: The URL for email verification.
        """

        subject = "Create Account"
        # Create HTML content inline
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Create Account</title>
                </head>
                <body>
                    <h2>Welcome to Our Platform!</h2>
                    <a href="{verification_link}" target="_blank">Complete Account</a>
                    <p>Please use this link to complete your account.</p>
                    <p>If you did not sign up for this account, please ignore this email.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>Your Company Team</p>
                </body>
                </html>
                """
        # Convert HTML to plain text for fallback
        text_content = strip_tags(html_content)

        # Create the email object
        email = EmailMultiAlternatives(subject, text_content, from_email=config("FROM_EMAIL"), to=recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Send email in a separate thread to avoid blocking the request
        threading.Thread(target=email.send).start()
