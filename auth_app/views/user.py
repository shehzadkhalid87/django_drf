from rest_framework import status
from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from auth_app.repositories.user import UserRepository
from auth_app.serializers.auth import UserSerializer, UserUpdateSerializer, UserProfilePictureSerializer, \
    ImportUsersSerializer, UpdateProfileSerializer
from auth_app.services.user import UserService
from core.base.base_view import BaseView
from core.decorators.api_response import api_response
from core.decorators.authentication import login_required
from core.decorators.authorization import authorization
from core.decorators.get_user_from_request import get_user_from_request
from core.decorators.pagination_decorator import paginate_list_view
from core.enums.enums import ROLES, ACCOUNT_STATUS
from core.utils.helper import generate_password


# admin view api only
@paginate_list_view
class ListAllUser(ListAPIView):
    """
    API View to list all users.
    This view is only accessible to users with 'view_users' permission.

    Pagination is applied via the @paginate_list_view decorator.
    """

    queryset = UserRepository.find()  # Fetch all users from the UserRepository
    serializer_class = UserSerializer  # Use UserSerializer to serialize the user data

    @api_response
    @authorization([ROLES.SUPER_ADMIN.value[0], ROLES.COMPANY.value[0]], ["list_users"])
    def get(self, request, *args, **kwargs):
        """
        Handles GET request to list all users.
        This method requires the 'view_users' permission for authorized access.

        :param request: Request object containing the HTTP request data
        :return: Paginated list of users serialized by UserSerializer
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filters queryset based on user role:
        - SUPER_ADMIN: Can view all users.
        - COMPANY: Can view only users associated by their company (the user).
        """
        user = self.request.user

        if user.role == ROLES.SUPER_ADMIN.value[0]:
            # SUPER_ADMIN can see all users
            return UserRepository.find()

        if user.role == ROLES.COMPANY.value[0]:
            # COMPANY can only see user they associated (where company is the user)
            return UserRepository.find().filter(organization=user)  # Or filter(company=user)

        return UserRepository.find().none()  # In case no role matches, return an empty queryset


class UserUpdateView(BaseView):
    """
    API View to block or unblock a user.
    """
    serializer_class = UserUpdateSerializer

    @api_response
    @authorization(groups=["super_admin"], permissions=["edit_user"])
    def post(self, request: Request):
        """
        Post method to either block or unblock the user based on action.
        :param request: HTTP request with user ID and action ('block' or 'unblock')
        """
        validated_data = self.validate_serializer(request)

        return Response({"success":
                             True if UserSerializer(instance=UserService.update_user_action_fields(data=validated_data))
                             else False
                         })


class UserProfileView(BaseView):
    """
    Update user profile data. this view mainly available
    for authenticated user.
    """

    @api_response
    @login_required
    @get_user_from_request
    def get(self, request: Request):
        """
        Retrieve the user's profile.

        This method serializes the user instance and returns the user's profile data.

        :param request: The HTTP request object.
        :return: Response containing the user's profile data.
        """
        user = UserSerializer(instance=request.user).data
        return Response({"user": user})


class UserProfileUpdatePicture(BaseView):
    """
    Upload profile picture for user.
    """
    serializer_class = UserProfilePictureSerializer  # Ensure you set this to your serializer

    @api_response
    @login_required
    @get_user_from_request
    def post(self, request: Request):
        """
        Update the user's profile picture.

        This method validates the request data and updates the user's profile
        picture if the data is valid.

        :param request: The HTTP request object containing the new picture data.
        :return: Response indicating the result of the update operation.

        :raises ValidationError: If the provided data is invalid.
        """
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile picture updated successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(DestroyAPIView):
    """
    View to delete user.
    View allow users to delete users, this view is available for
    super admin only for right now.
    """

    @api_response
    @authorization(groups=[ROLES.SUPER_ADMIN.value[0]], permissions=["delete_user"])
    def delete(self, request, *args, **kwargs) -> Response:
        """
        :param request:
        :param args:
        :param kwargs:
        :return: Response
        """
        # Extract the user ID from the URL
        return Response(
            {"success": True if UserSerializer(instance=UserService.delete_user(kwargs.get('id'))) else False},
            status=status.HTTP_204_NO_CONTENT
        )


class ImportUsers(BaseView):
    """
    View to add import user from a csv file.

    This view allows organizer or company to add users by
    uploading csv file.
    """
    serializer_class = ImportUsersSerializer

    @api_response
    @authorization(groups=[ROLES.COMPANY.value[0]], permissions=["import_users"])
    def post(self, request: Request) -> Response:
        """
        post request
        :param request:
        :return: Response
        """
        validated_data = self.validate_serializer(request)

        UserService.import_user(validated_data, request.user)
        return Response({"message": "Users imported successfully"})


class AddUserView(BaseView):
    """
    View for adding a new user to the system.

    This view allows users with the role of COMPANY to create new users in the system.
    It automatically assigns the role of CANDIDATE and generates a password for the new user.
    """

    serializer_class = ImportUsersSerializer

    @api_response
    @authorization(groups=[ROLES.COMPANY.value[0]], permissions=["add_user"])
    def post(self, request: Request):
        """
        Create a new user.

        :param request: The HTTP request containing the user data for registration.
        :return: Response indicating the success of the user creation.
        :raises ApiError: If validation fails or if the user does not have permission.
        """
        ser = self.get_serializer_class()
        ser.initial_data['role'] = ROLES.CANDIDATE.value[0]  # Set additional fields
        ser.initial_data['password'] = generate_password()  # Generate a random password
        ser.initial_data['status'] = ACCOUNT_STATUS.PENDING.value[0]  # Set additional fields
        ser.initial_data['company'] = request.user.pk  # Associate user with the company

        validated_data = self.validate_serializer(request)
        UserService.add_user_manual(validated_data)
        return Response({"message": "User created successfully"})


class GetUser(BaseView):
    """
    API View for retrieving user details. Accessible only to users with 'view_user' permission.
    Organizers can only view users within their company or their own details.
    Super Admins can view any user.
    """

    @api_response
    @authorization(groups=[
        ROLES.SUPER_ADMIN.value[0], ROLES.COMPANY.value[0]],
        permissions=["view_user"])
    def get(self, request: Request, user_id: int):
        """
        Handle GET request to retrieve user information.
        """
        return Response({"user": UserService.get_user(request.user, user_id)})


class UpdateProfileView(BaseView):
    """
    View for updating user profile information.

    This view allows users to update their profile data. It requires the user to be authenticated
    and to have the appropriate permissions based on their role.
    """

    serializer_class = UpdateProfileSerializer

    @api_response
    @authorization(groups=[
        ROLES.SUPER_ADMIN.value[0], ROLES.EDUCATOR.value[0],
        ROLES.CANDIDATE.value[0], ROLES.COMPANY.value[0], ROLES.EDUCATOR.value[0]
    ], permissions=["update_profile"])
    def patch(self, request: Request):
        """
        Update the user's profile information.

        :param request: The HTTP request containing user data to update.
        :return: Response with updated user data.
        :raises ApiError: If validation fails or if the user does not have permission.
        """
        user = request.user
        validated_data = self.validate_serializer(request)
        updated_user = UserService.update_user(user.pk, validated_data)
        return Response(UserSerializer(instance=updated_user).data)
