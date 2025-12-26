from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .utils import decrypt_login_password


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": _(
            "无效的用户名或密码"
        ),
        "inactive": _("该账户已被禁用"),
    }

    def clean(self):
        enc_flag = (self.data.get('enc', '') or '').strip() == '1'
        password_cipher = (self.data.get('password') or '').strip()
        if enc_flag and password_cipher:
            try:
                plaintext = decrypt_login_password(password_cipher)
                # Overwrite both data and cleaned_data so AuthenticationForm authenticates plaintext
                mutable_data = self.data.copy()
                mutable_data['password'] = plaintext
                self.data = mutable_data
                if hasattr(self, 'cleaned_data'):
                    self.cleaned_data['password'] = plaintext
            except Exception as exc:  # pragma: no cover - decrypt failures
                raise ValidationError(_('无法解密密码，请重试或联系管理员。')) from exc
        return super().clean()


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

    def clean_new_password1(self):
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')
        if old_password and new_password1 and old_password == new_password1:
            raise ValidationError(_('新密码不能与当前密码相同'))
        return new_password1
