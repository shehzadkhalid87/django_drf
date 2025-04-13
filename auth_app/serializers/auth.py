from typing import Any, Dict

from rest_framework import serializers

from auth_app.models import UserEntity
from core.enums.enums import ROLES, USER_UPDATE_ACTIONS  # Import the regular expression module
from core.utils.helper import validate_password


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for UserEntity model. This serializer is used for retrieving user details,
    including read-only fields like 'created_at' and 'updated_at'.
    """

    class Meta:
        """
        Serializer for UserEntity
        """
        model = UserEntity
        fields = [
            "id", "full_name", "email", "role",
            "trade_name", "corporate_name", "city",
            "numbers_employees", "cnpj", "cpf", "profession",
            "phone_number", "created_at", "last_login", "profile_picture",
            "company", "numbers_employees"
        ]
        read_only_fields = ["created_at", "updated_at"]  # Fields that are not editable by the user


class SignupSerializer(serializers.Serializer):
    """
    Serializer for user registration (signup) functionality. Validates the data provided
    for user creation, such as first name, last name, email, password, and other personal details.
    """
    full_name = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Full name should not be empty."}
    )
    email = serializers.EmailField(
        write_only=True,
        required=True,
        error_messages={"required": "Email should not be empty."}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Password should not be empty."}
    )
    role = serializers.ChoiceField(
        choices=ROLES.choices(),
        required=True,
        error_messages={"required": "Role should not be empty."}
    )
    trade_name = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={"required": "Trades should not be empty."}
    )  # required for company
    corporate_name = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={"required": "Corporate name should not be empty."}
    )  # required for company
    numbers_employees = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={"required": "Number of employees should not be empty."}
    )
    city = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "City should not be empty."}
    )
    cnpj = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={"required": "CNPJ name should not be empty."}
    )  # required for company
    cpf = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={"required": "CPF name should not be empty."}
    )  # required for educator
    profession = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Profession number should not be empty."}
    )
    phone_number = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Phone number should not be empty."}
    )
    status = serializers.CharField(max_length=128, required=False)
    is_agreement_accepted = serializers.BooleanField(
        required=True,
        error_messages={"required": "Please agree the terms and conditions"}
    )
    company = serializers.PrimaryKeyRelatedField(queryset=UserEntity.objects.all(), required=False)

    class Meta:
        """
        Metaclass defining the fields used for user registration.
        """
        fields = [
            "full_name", "email", "role",
            "trade_name", "corporate_name", "city",
            "numbers_employees", "cnpj", "cpf", "profession",
            "phone_number",
        ]

    def validate_password(self, value: str) -> str:
        return validate_password(value)

    def validate_role(self, value: str) -> str:
        """
        Validate the role field to prevent certain roles like 'CANDIDATE' or 'SUPER_ADMIN'
        from registering through the standard registration process.
        """
        if value in [ROLES.CANDIDATE.value, ROLES.SUPER_ADMIN.value]:
            raise serializers.ValidationError(f"{value} cannot signup via registration process.", value)

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform additional validation based on the role. For example:
        """
        # Remove extra fields not defined in the serializer
        role = data.get("role", None)
        if role in [ROLES.SUPER_ADMIN.value, ROLES.CANDIDATE.value]:
            raise serializers.ValidationError({"non_field_errors": ["Operation not allowed."]})

        cnpj = data.get("cnpj")
        cpf = data.get("cpf")
        trades = data.get("trade_name")
        corporate = data.get("corporate_name")
        number_emp = data.get("numbers_employees")

        # Check for COMPANY role and validate fields
        if role == ROLES.COMPANY.value[0]:
            errors = {}
            if not cnpj:
                errors["cnpj"] = ["CNPJ is not allowed to be empty."]
            if not trades:
                errors["trade_name"] = ["Trades is not allowed to be empty."]
            if not corporate:
                errors["corporate_name"] = ["Corporate name is not allowed to be empty."]
            if not number_emp:
                errors["numbers_employees"] = ["Number of employees is not allowed to be empty."]
            if errors:
                raise serializers.ValidationError(errors)

        # Check for EDUCATOR role and validate fields
        if role == ROLES.EDUCATOR.value[0]:
            if not cpf:
                raise serializers.ValidationError({"cpf": ["CPF is not allowed to be empty."]})

        return data

    def validate_is_agreement_accepted(self, value):
        if value is not True:
            raise serializers.ValidationError("You must accept the agreement.")
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login functionality. Accepts 'email' and 'password' as inputs.
    """
    email = serializers.EmailField(write_only=True, required=True,
                                   error_messages={"required": "Email must not be empty."})
    password = serializers.CharField(write_only=True, required=True,
                                     error_messages={"required": "Password must not be empty."})


class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for handling token refresh. Accepts a 'refresh' token to issue a new token.
    """
    refresh = serializers.CharField(write_only=True, required=True)


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification. Accepts a 'token' and 'uid' for verification purposes.
    """
    token = serializers.CharField(write_only=True, required=True, error_messages={"required": "token is required."})
    uid = serializers.CharField(
        write_only=True,
        required=True,
        max_length=2,
        error_messages={
            "max_length": "Invalid length of uid.",
            "blank": "This field cannot be blank.",
            "required": "uid is required."
        }
    )


class CandidateAccountSerializer(serializers.Serializer):
    """
    Serializer for email verification. Accepts a 'token' and 'uid' for verification purposes.
    """
    token = serializers.CharField(write_only=True, required=True)
    uid = serializers.CharField(
        write_only=True,
        required=True,
        max_length=2,
        error_messages={
            "max_length": "Invalid length of uid.",
            "blank": "This field cannot be blank.",
            "required": "This field is required."
        }
    )
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value: str) -> str:
        return validate_password(value)


class UserUpdateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(write_only=True, required=True, error_messages={
        "required": "User id is required"
    })
    action = serializers.ChoiceField(write_only=True, choices=USER_UPDATE_ACTIONS.choices(), required=True,
                                     error_messages={"required": "Action id is required"})

    def to_internal_value(self, data):
        # Call the parent to_internal_value to ensure other validations are done
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as error:
            available_options = "(" + ', '.join(tag.value for tag in USER_UPDATE_ACTIONS) + ")"
            if 'action' in error.detail:
                # Customize the error message for the 'action' field
                raise serializers.ValidationError(
                    {
                        "action": f"Invalid action. Available options are: {available_options}."
                    }
                )
            raise error from error


class UserProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=True)

    class Meta:
        model = UserEntity
        fields = ['profile_picture']


class ImportUsersSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class UpdateProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(write_only=True, required=False, max_length=256)
    profession = serializers.CharField(write_only=True, required=False, max_length=128)
    phone_number = serializers.CharField(write_only=True, required=False, max_length=15)
    trade_name = serializers.CharField(write_only=True, required=False, max_length=256)
    city = serializers.CharField(write_only=True, required=False, max_length=128)
    cnpj = serializers.CharField(write_only=True, required=False, max_length=128)
    cpf = serializers.CharField(write_only=True, required=False, max_length=128)
    corporate_name = serializers.CharField(write_only=True, required=False, max_length=256)
    city = serializers.CharField(write_only=True, required=False)
    numbers_employees = serializers.IntegerField(write_only=True, required=False)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True,
                                         error_messages={"required": "OLD Password must not be empty."})
    password = serializers.CharField(write_only=True, required=True,
                                     error_messages={"required": "Password must not be empty."})

    def validate_password(self, value: str) -> str:
        return validate_password(value)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, required=True,
                                  error_messages={"required": "Email must not be empty."})


class ResetPasswordSerializer(EmailVerificationSerializer):
    password = serializers.CharField(write_only=True, required=True,
                                     error_messages={"required": "Password must not be empty."})

    def validate_password(self, value: str) -> str:
        return validate_password(value)
