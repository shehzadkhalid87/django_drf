from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Replace six.text_type with str
        return str(user.pk) + str(timestamp) + str(user.is_active)


email_verification_token = EmailVerificationTokenGenerator()
