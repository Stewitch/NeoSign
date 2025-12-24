from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomAuthenticationForm(AuthenticationForm):
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return password
        if len(password) < 8:
            raise ValidationError('密码长度至少8位')
        if not any(char.isdigit() for char in password):
            raise ValidationError('密码必须包含数字')
        if not any(char.isalpha() for char in password):
            raise ValidationError('密码必须包含字母')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise ValidationError('密码必须包含特殊字符')
        return password


class RequiredPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and translated placeholders
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('当前密码'),
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('新密码'),
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('确认新密码'),
        })
