# your_app/management/commands/helper_command.py
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create groups and permissions'

    def handle(self, *args, **kwargs):
        # Define your groups and their associated permissions
        pass
