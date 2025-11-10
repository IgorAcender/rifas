from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Update admin user email and password'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email address')
        parser.add_argument('--password', type=str, help='Admin password (optional)')

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')

        if not email:
            self.stdout.write(self.style.ERROR('❌ Email is required. Use: --email seu@email.com'))
            return

        try:
            # Buscar o primeiro admin/superuser
            admin = User.objects.filter(is_staff=True).first()
            
            if not admin:
                self.stdout.write(self.style.ERROR('❌ No admin user found'))
                return

            # Atualizar email
            admin.email = email
            
            # Atualizar senha se fornecida
            if password:
                admin.set_password(password)
                self.stdout.write(self.style.SUCCESS(f'✅ Admin updated: {admin.name}'))
                self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
                self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ Admin email updated: {admin.name}'))
                self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
                self.stdout.write(self.style.WARNING('⚠️  Password not changed'))
            
            admin.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error updating admin: {e}'))
            raise
