from django.core.exceptions import ValidationError


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise ValidationError('密码必须包含至少一个特殊字符')

    def get_help_text(self):
        return '密码必须包含至少一个特殊字符'
