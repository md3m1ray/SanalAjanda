from django.core.management.base import BaseCommand
from django.utils.timezone import now
from users.models import User

class Command(BaseCommand):
    help = 'Downgrade expired memberships to Standard'

    def handle(self, *args, **kwargs):
        expired_users = User.objects.filter(
            membership_expiry__lt=now(),
            membership_level__in=['Premium', 'Gold', 'Platinum']
        )
        for user in expired_users:
            user.membership_level = 'Standard'
            user.membership_expiry = None
            user.save()
            self.stdout.write(f"Downgraded {user.username} to Standard membership.")
