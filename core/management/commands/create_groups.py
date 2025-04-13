# your_app/management/commands/create_groups.py
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create groups and permissions'

    def handle(self, *args, **kwargs):
        # Define your groups and their associated permissions
        groups_permissions = {
            'SUPER_AMDIN': [
                'auth_app.add_user',
                'auth_app.change_user',
                'auth_app.delete_user',
                'auth_app.view_user',
                # Add more permissions as needed
            ],
            'ORGANIZATION': [
                'your_app.add_team',  # Replace with actual permission names
                'your_app.send_assessment',
                'your_app.view_assessment',
                'your_app.view_results',
                # Add more permissions as needed
            ],
            'EDUCATOR': [
                'your_app.attempt_assessment',
                'your_app.view_own_results',
                # Add more permissions as needed
            ],
            'CANDIDATE': [
                'your_app.attempt_assessment',
                'your_app.view_own_results',
                # Add more permissions as needed
            ],
        }

        # Create groups and permissions
        for group_name, permissions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created.'))

            # Add permissions to the group
            for perm_name in permissions:
                try:
                    app_label, codename = perm_name.split('.')
                    permission = Permission.objects.get(codename=codename, content_type__app_label=app_label)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Permission "{perm_name}" does not exist.'))

        self.stdout.write(self.style.SUCCESS('Groups and permissions have been created/updated.'))
