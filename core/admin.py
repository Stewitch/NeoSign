from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, SystemConfig


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'is_active', 'is_admin', 'is_staff', 'first_login')
    list_filter = ('is_active', 'is_admin', 'is_staff', 'first_login')
    ordering = ('username',)
    search_fields = ('username', 'first_name')
    readonly_fields = ('created_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name',)}),
        (_('权限'), {
            'fields': (
                'is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        (_('重要日期'), {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_admin', 'is_staff', 'is_superuser'),
        }),
    )

    def get_ordering(self, request):  # runtime-safe ordering
        return ('username',)

    def get_list_display(self, request):
        return ('username', 'first_name', 'is_active', 'is_admin', 'is_staff', 'first_login')


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'installed', 'technician_contact')
