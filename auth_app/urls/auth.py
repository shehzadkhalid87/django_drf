from django.urls import path

from auth_app.views.auth import LoginView, RefreshTokenView, EmailVerificationView, LoginSuperAdmin, \
    CandidateAccountCompleteView, SignupView, ResetPasswordView, ForgotPasswordView, ChangePasswordView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup_api"),
    path("login/", LoginView.as_view(), name="login_api"),
    path("admin/login/", LoginSuperAdmin.as_view(), name="super_admin_login"),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path("email/verify/", EmailVerificationView.as_view(), name="verify_email"),
    path(
        "candidate/account/",
        CandidateAccountCompleteView.as_view(), name="candidate_account_process"),
    path("account/forgot/password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("account/reset/password/", ResetPasswordView.as_view(), name="reset_password"),
    path("password/change/", ChangePasswordView.as_view(), name="change_password"),
]
