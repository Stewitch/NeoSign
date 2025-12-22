from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, SystemConfig


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('student_id', 'first_name', 'is_active', 'is_admin', 'is_staff', 'first_login')
    list_filter = ('is_active', 'is_admin', 'is_staff', 'first_login')
    ordering = ('student_id',)
    search_fields = ('student_id', 'first_name')
    readonly_fields = ('created_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('student_id', 'password')}),
        (_('Personal info'), {'fields': ('first_name',)}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'password1', 'password2', 'is_admin', 'is_staff', 'is_superuser'),
        }),
    )


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'installed', 'technician_contact')
