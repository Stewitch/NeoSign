from django import template
from math import ceil

register = template.Library()


def _mask_middle(value: str) -> str:
    if not value:
        return ''
    n = len(value)
    if n <= 2:
        return value[0] + '*' * (n - 1)
    mask_len = max(1, ceil(n / 3))
    start = max(1, (n - mask_len) // 2)
    end = min(n, start + mask_len)
    return value[:start] + ('*' * (end - start)) + value[end:]


@register.simple_tag
def mask_field(value, field_type, context, config):
    """通用字段脱敏标签，支持上下文感知
    
    Args:
        value: 要处理的值（学号或姓名）
        field_type: 'student_id' 或 'name'
        context: 'frontend' 或 'admin'
        config: SystemConfig 实例
    """
    if not value:
        return '-'
    
    if not config:
        return value
    
    masking_mode = getattr(config, 'username_masking_mode', 'frontend')
    
    # 根据模式和上下文决定是否脱敏
    should_mask = False
    if masking_mode == 'both':
        should_mask = True
    elif masking_mode == 'frontend' and context == 'frontend':
        should_mask = True
    
    if should_mask:
        return _mask_middle(str(value))
    return value


def _build_display(user, config, context: str) -> str:
    display_mode = getattr(config, 'username_display_mode', 'student_id') if config else 'student_id'
    mask_mode = getattr(config, 'username_masking_mode', 'frontend') if config else 'frontend'

    def _should_mask():
        if mask_mode == 'none':
            return False
        if mask_mode == 'frontend' and context == 'frontend':
            return True
        if mask_mode == 'both' and context in ('frontend', 'admin'):
            return True
        return False

    parts = []
    if display_mode == 'student_id':
        parts.append(user.student_id)
    elif display_mode == 'name':
        parts.append(user.first_name or '')
    else:  # both
        parts.append(user.student_id)
        parts.append(user.first_name or '')

    joined = ' '.join(p for p in parts if p)
    if not joined:
        return ''
    return _mask_middle(joined) if _should_mask() else joined


@register.filter(name='display_user')
def display_user(user, args):
    """
    Usage: {{ user|display_user:"context,config" }}
    context: 'frontend' or 'admin'
    config: pass in template via with or variable
    Example: {{ user|display_user:frontend_config }} (see below helper tag)
    """
    if not user:
        return ''
    # args expected tuple-like (context, config)
    if isinstance(args, (list, tuple)) and len(args) == 2:
        context, config = args
    else:
        # fallback: if a string passed, assume context; no config
        context, config = (args, None)
    return _build_display(user, config, context or 'frontend')


@register.simple_tag
def user_display(user, context, config=None):
    """Template tag for clearer call: {% user_display user 'frontend' config %}"""
    if not user:
        return ''
    return _build_display(user, config, context)
