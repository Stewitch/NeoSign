from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError


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
    pass
