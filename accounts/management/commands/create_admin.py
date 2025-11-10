from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import User


class Command(BaseCommand):
    help = 'Create admin user from environment variables'

    def handle(self, *args, **options):
        whatsapp = settings.ADMIN_WHATSAPP
        password = settings.ADMIN_PASSWORD
        name = settings.ADMIN_NAME
        email = getattr(settings, 'ADMIN_EMAIL', None)

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('✅ Admin user already exists'))
            return

        try:
            user = User.objects.create_superuser(
                whatsapp=whatsapp,
                name=name,
                password=password,
                email=email
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Admin user created: Email={email}, Password={password}'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating admin: {e}'))
            raise
