from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('whatsapp', 'name', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('whatsapp', 'name', 'email')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('whatsapp', 'password')}),
        ('Informacoes Pessoais', {'fields': ('name', 'email')}),
        ('Permissoes', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('whatsapp', 'name', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')
