from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, student_id: str, password: str | None = None, **extra_fields):
        if not student_id or not student_id.isdigit() or not (4 <= len(student_id) <= 23):
            raise ValueError('学号必须是4-23位数字')

        user = self.model(student_id=student_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(student_id, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    student_id = models.CharField(
        max_length=23,
        unique=True,
        validators=[RegexValidator(r'^\d{4,23}$', '学号必须是4-23位数字')],
        verbose_name='学号',
    )
    first_name = models.CharField(max_length=50, blank=True, verbose_name='姓名')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_staff = models.BooleanField(default=False, verbose_name='后台管理员')
    is_admin = models.BooleanField(default=False, verbose_name='系统管理员')
    first_login = models.BooleanField(default=True, verbose_name='首次登录')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='上次登录时间')

    objects = CustomUserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-created_at']

    def __str__(self) -> str:  # pragma: no cover - simple display
        return self.student_id


class SystemConfig(models.Model):
    site_title = models.CharField(max_length=100, default='签到系统', verbose_name='站点标题')
    site_logo = models.ImageField(upload_to='system/logo/', null=True, blank=True, verbose_name='站点Logo')
    technician_contact = models.CharField(max_length=100, blank=True, verbose_name='技术支持联系方式')
    map_api_key = models.CharField(max_length=200, blank=True, verbose_name='地图 API Key')
    installed = models.BooleanField(default=False, verbose_name='是否已安装')
    db_host = models.CharField(max_length=100, blank=True, verbose_name='数据库地址')
    db_name = models.CharField(max_length=100, blank=True, verbose_name='数据库名称')
    db_user = models.CharField(max_length=100, blank=True, verbose_name='数据库用户名')
    # 密码策略
    password_length = models.PositiveSmallIntegerField(default=12, verbose_name='初始密码长度')
    password_require_uppercase = models.BooleanField(default=True, verbose_name='包含大写字母')
    password_require_lowercase = models.BooleanField(default=True, verbose_name='包含小写字母')
    password_require_digits = models.BooleanField(default=True, verbose_name='包含数字')
    password_require_symbols = models.BooleanField(default=True, verbose_name='包含符号')
    password_symbols = models.CharField(
        max_length=50,
        default='!@#$%^&*',
        blank=True,
        verbose_name='符号字符集合'
    )

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'

    def __str__(self) -> str:  # pragma: no cover - simple display
        return self.site_title
