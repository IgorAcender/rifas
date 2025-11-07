from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for WhatsApp-based authentication"""

    def create_user(self, whatsapp, name=None, **extra_fields):
        """Create and save a regular user"""
        if not whatsapp:
            raise ValueError('WhatsApp number is required')

        whatsapp = self.normalize_whatsapp(whatsapp)
        user = self.model(
            whatsapp=whatsapp,
            name=name or whatsapp,
            **extra_fields
        )
        user.set_unusable_password()  # No password for regular users
        user.save(using=self._db)
        return user

    def create_superuser(self, whatsapp, name=None, password=None, **extra_fields):
        """Create and save a superuser (admin with password)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not whatsapp:
            raise ValueError('WhatsApp number is required')

        whatsapp = self.normalize_whatsapp(whatsapp)
        user = self.model(
            whatsapp=whatsapp,
            name=name or 'Admin',
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    @staticmethod
    def normalize_whatsapp(whatsapp):
        """Remove special characters from WhatsApp number"""
        return ''.join(filter(str.isdigit, whatsapp))


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using WhatsApp as primary identifier.
    Regular users: WhatsApp only (no password)
    Admin: WhatsApp + password
    """
    whatsapp = models.CharField(
        'WhatsApp',
        max_length=20,
        unique=True,
        help_text='Numero de WhatsApp (apenas digitos)'
    )
    name = models.CharField('Nome', max_length=150)
    email = models.EmailField('Email', unique=True, blank=True, null=True)
    cpf = models.CharField('CPF', max_length=14, unique=True, blank=True, null=True)

    is_active = models.BooleanField('Ativo', default=True)
    is_staff = models.BooleanField('Admin', default=False)

    date_joined = models.DateTimeField('Data de cadastro', default=timezone.now)
    last_login = models.DateTimeField('Ultimo acesso', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'whatsapp'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.name} ({self.whatsapp})"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split()[0] if self.name else self.whatsapp
