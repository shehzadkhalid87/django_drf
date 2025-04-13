from django.urls import path

from auth_app.views.user import ListAllUser, UserUpdateView, UserProfileView, UserProfileUpdatePicture, \
    UserDeleteView, ImportUsers, AddUserView, GetUser, UpdateProfileView

urlpatterns = [
    path("admin/edit/user/", UserUpdateView.as_view(), name="super_admin_edit_user"),
    path("list/", ListAllUser.as_view(), name="list_all_users"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/picture/", UserProfileUpdatePicture.as_view(), name="upload_profile_picture"),
    path("admin/delete/<int:id>/", UserDeleteView.as_view(), name="user_delete_view"),
    path("teams/import/", ImportUsers.as_view(), name="import_users"),
    path("candidate/account/add/", AddUserView.as_view(), name="add_user"),
    path("view/<int:user_id>/", GetUser.as_view(), name="view_user"),
    path("profile/edit/", UpdateProfileView.as_view(), name="update_profile"),
]
