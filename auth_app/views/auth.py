from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from auth_app.serializers.auth import SignupSerializer, LoginSerializer, RefreshTokenSerializer, \
    EmailVerificationSerializer, CandidateAccountSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, \
    ChangePasswordSerializer
from auth_app.services.user import UserService
from core.base import BaseView
from core.decorators.api_response import api_response
from core.decorators.authentication import login_required
from core.decorators.get_user_from_request import get_user_from_request


class SignupView(BaseView):
    """
    Signup view
    >> path("signup/", SignupView.as_view(), name="any")
    """

    serializer_class = SignupSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        API Method: POST
        create new user
        """
        validated_data = self.validate_serializer(request)
        # Create the user entity
        UserService.signup_user(validated_data)
        return Response({"message": "successfully registered the user."})


class LoginView(BaseView):
    """
    Login View
    >> LoginView.as_view()
    >> path("login/", LoginView.as_view(), name="any")
    """
    serializer_class = LoginSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        :param: request[Request]
        :return:  LoginResult
        """
        validated_data = self.validate_serializer(request)

        result = UserService.login_user(validated_data)
        return Response(result.to_dict())


class RefreshTokenView(BaseView, TokenViewBase):
    """
    Request for a new access token on existing token expiration.
    >> path("token/refresh/", RefreshTokenView.as_view(), name="any")
    """
    serializer_class = RefreshTokenSerializer

    @api_response
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        :param: request[Request]
        :return: access token from refresh token
        """
        validated_data = self.validate_serializer(request)

        return Response(UserService.refresh_token(validated_data).to_dict())


class EmailVerificationView(BaseView):
    """
    API View to handle the email verification process.

    This view processes POST requests from users who click on a verification link in their email.
    The link contains a user ID (uid) and a token that is validated here. If valid, the user's
    email verification status is updated, and a welcome email is sent.

    The token is marked as used to prevent reuse, and appropriate error messages are returned
    in case of invalid links or requests.
    """
    serializer_class = EmailVerificationSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        Handle POST request for email verification.

        This method takes the user's uid and token from the request data,
        decodes and verifies the uid, and checks if the token is valid.
        If everything is valid, the user's email verification
        status is updated, and a welcome email is sent. Otherwise,
        appropriate errors are returned.

        :param request: Request object containing the user's uid and token.
        :return: Success response if the verification is successful, error otherwise.
        """
        # Deserialize and validate incoming data from the request
        validated_data = self.validate_serializer(request)

        return Response(UserService.verify_email(validated_data).to_dict())


class LoginSuperAdmin(BaseView):
    """
    Login Super View
    >> LoginView.as_view()
    >> path("login/", LoginSuperAdmin.as_view(), name="any")
    """
    serializer_class = LoginSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        :param: request[Request]
        :return:  LoginResult
        """
        validated_data = self.validate_serializer(request)

        result = UserService.login_user(validated_data)
        return Response(result.to_dict())


class CandidateAccountCompleteView(BaseView):
    """
    API View to handle candidate account process.
    Users receive a verification link containing a token and uid which is verified here.
    """

    serializer_class = CandidateAccountSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        Handles POST request to verify a user's email.

        The method validates the provided uid and token from the verification email,
        decodes the uid, checks the token, and if valid, marks the user's email as verified.

        :param request: Request object containing the HTTP request data
        :return: Success message on valid verification, or raises an error on failure
        """
        validated_data = self.validate_serializer(request)

        return Response(
            UserService.complete_candidate_account(validated_data)
        )


class ForgotPasswordView(BaseView):
    """
    API View to initiate a forgot password process.

    Users provide their registered email to receive a password reset link.
    If the email is associated with an account, a reset link is sent to the user's email.

    :param request: Request object containing the email data
    :return: Success message indicating the reset link has been sent,
    or raises an error if the email is invalid
    """

    serializer_class = ForgotPasswordSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        Handles POST request for initiating a forgot password request.

        This method validates the provided email, checks if it is registered,
        and initiates the password reset process by sending a reset link.

        :param request: Request object containing the HTTP request data
        :return: Success message on request initiation, or raises an error if email is not found
        """
        validated_data = self.validate_serializer(request)

        return Response({"success": UserService.forgot_password_request(validated_data.get("email"))})


class ResetPasswordView(BaseView):
    """
    API View to handle password reset requests.

    Users provide a new password along with their reset token,
    enabling them to reset their password.
    This process finalizes the password change based on the token validation.

    :param request: Request object containing the new password and reset token
    :return: Success message indicating the password has been reset,
    or raises an error if the token is invalid
    """

    serializer_class = ResetPasswordSerializer

    @api_response
    def post(self, request: Request) -> Response:
        """
        Handles POST request to reset a user's password.

        The method validates the provided token and new password,
        and if valid, updates the user's password in the system.

        :param request: Request object containing the HTTP request data
        :return: Success message on successful password reset, or raises an error on failure
        """
        validated_data = self.validate_serializer(request)

        return Response({"success": UserService.reset_password_request(validated_data)})


class ChangePasswordView(BaseView):
    """
    View for changing the user's password.

    This view allows authenticated users to change their password.
    It ensures that the user provides their old password and a new password.
    """
    serializer_class = ChangePasswordSerializer

    @api_response
    @login_required
    @get_user_from_request
    def post(self, request: Request):
        """
        Change the user's password.

        :param request: The HTTP request containing the old and new password.
        :return: Response indicating success or failure of password change.
        :raises ApiError: If validation fails or if the old password is incorrect.
        """
        validated_data = self.validate_serializer(request)

        UserService.change_password(request.user, validated_data)
        return Response({"message": "password updated successfully"})
