# Django签到系统开发任务描述

## 项目概述
使用Django框架开发一个学校线上培训活动签到系统，满足高安全性要求，具备完整的安装、登录、签到和管理功能。

## 技术栈
- **后端**: Django 6.0
- **数据库**: PostgreSQL
- **前端**: Django模板 + Bootstrap 5 + JavaScript
- **认证**: Django内置认证系统 + 自定义用户模型
- **安全**: Django安全中间件 + CSRF保护 + 密码哈希

## 项目结构规划

**注意：请先读取当前项目结构，并根据现有结构适当调整，请不要破坏当前的项目结构，由 Django 自动生成**

```
sign_system/
├── config/                 # Django配置
│   ├── settings/
│   │   ├── base.py        # 基础配置
│   │   ├── development.py # 开发环境
│   │   └── production.py  # 生产环境
│   └── wsgi.py
├── apps/
│   ├── core/              # 核心应用
│   │   ├── models.py      # 自定义用户模型
│   │   ├── admin.py       # 管理后台配置
│   │   └── views.py
│   ├── installation/      # 安装应用
│   ├── authentication/    # 认证应用
│   ├── checkin/          # 签到应用
│   ├── management/       # 管理应用
│   └── api/              # API接口（可选）
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
│   ├── uploads/
│   └── exports/
├── templates/
│   ├── base.html
│   ├── installation/
│   ├── authentication/
│   ├── checkin/
│   └── management/
├── requirements.txt
└── manage.py
```

## 数据模型设计

### 1. 自定义用户模型 (CustomUser)
```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, student_id, password=None, **extra_fields):
        # 验证学号：10位纯数字
        if not student_id or not student_id.isdigit() or len(student_id) != 10:
            raise ValueError('学号必须是10位数字')
        
        user = self.model(student_id=student_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, student_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(student_id, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    student_id = models.CharField(max_length=10, unique=True, validators=[
        RegexValidator(r'^\d{10}$', '学号必须是10位数字')
    ])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)  # 系统管理员
    first_login = models.BooleanField(default=True)  # 首次登录标识
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = []
```

### 2. 系统配置模型
```python
class SystemConfig(models.Model):
    site_title = models.CharField(max_length=100, default='签到系统')
    site_logo = models.ImageField(upload_to='system/logo/', null=True, blank=True)
    technician_contact = models.CharField(max_length=100)
    installed = models.BooleanField(default=False)
    db_host = models.CharField(max_length=100, blank=True)
    db_name = models.CharField(max_length=100, blank=True)
    db_user = models.CharField(max_length=100, blank=True)
    # 注意：数据库密码不存储在模型中，仅在安装时配置
    
    def __str__(self):
        return self.site_title
```

### 3. 活动模型
```python
class Activity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # 参与用户（多对多关系）
    participants = models.ManyToManyField(
        CustomUser, 
        through='ActivityParticipation',
        related_name='activities'
    )
    
    class Meta:
        verbose_name_plural = '活动'
        ordering = ['-start_time']
```

### 4. 活动参与模型
```python
class ActivityParticipation(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    can_participate = models.BooleanField(default=True)  # 是否允许参与
    
    class Meta:
        unique_together = ('activity', 'user')
```

### 5. 签到记录模型
```python
class CheckInRecord(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='checkins')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='checkins')
    checkin_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('activity', 'user')  # 防止重复签到
        ordering = ['-checkin_time']
```

## 核心功能实现

### 1. 安装系统
**应用**: `installation`
- **检测逻辑**: 检查`SystemConfig.objects.filter(installed=True).exists()`
- **安装流程**:
  1. 环境检查：Python版本、Django版本、数据库驱动
  2. 数据库配置：主机、端口、数据库名、用户名、密码
  3. 创建数据库表：`python manage.py migrate`
  4. 创建超级管理员账户
  5. 配置系统信息：网站标题、logo、联系方式
  6. 标记安装完成，生成配置文件
- **安全要求**: 安装完成后自动禁用安装路由

### 2. 认证系统
**应用**: `authentication`
- **登录视图**:
  ```python
  class CustomLoginView(LoginView):
      form_class = CustomAuthenticationForm
      template_name = 'authentication/login.html'
      
      def form_valid(self, form):
          response = super().form_valid(form)
          user = self.request.user
          
          # 记录登录时间
          user.last_login = timezone.now()
          user.save(update_fields=['last_login'])
          
          # 首次登录重定向到修改密码页面
          if user.first_login:
              messages.warning(self.request, '首次登录，请修改密码')
              return redirect('password_change_required')
          
          # 根据角色重定向
          if user.is_admin or user.is_superuser:
              return redirect('management:dashboard')
          else:
              return redirect('checkin:dashboard')
  ```

- **密码验证表单**:
  ```python
  class CustomAuthenticationForm(AuthenticationForm):
      def clean_password(self):
          password = self.cleaned_data.get('password')
          # 密码复杂度验证
          if len(password) < 8:
              raise ValidationError('密码长度至少8位')
          if not any(char.isdigit() for char in password):
              raise ValidationError('密码必须包含数字')
          if not any(char.isalpha() for char in password):
              raise ValidationError('密码必须包含字母')
          if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
              raise ValidationError('密码必须包含特殊字符')
          return password
  ```

- **强制修改密码视图**:
  ```python
  class RequiredPasswordChangeView(PasswordChangeView):
      template_name = 'authentication/password_change_required.html'
      
      def form_valid(self, form):
          response = super().form_valid(form)
          # 更新首次登录状态
          user = self.request.user
          user.first_login = False
          user.save(update_fields=['first_login'])
          messages.success(self.request, '密码修改成功')
          return response
      
      def dispatch(self, request, *args, **kwargs):
          # 只有首次登录的用户才需要强制修改密码
          if not request.user.first_login:
              return redirect('checkin:dashboard')
          return super().dispatch(request, *args, **kwargs)
  ```

### 3. 签到系统
**应用**: `checkin`
- **签到仪表板**:
  ```python
  class CheckInDashboardView(LoginRequiredMixin, TemplateView):
      template_name = 'checkin/dashboard.html'
      
      def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          user = self.request.user
          now = timezone.now()
          
          # 获取用户可参与的活动
          activities = Activity.objects.filter(
              participants=user,
              start_time__lte=now,
              end_time__gte=now,
              is_active=True
          ).select_related('created_by').prefetch_related('checkins')
          
          # 检查签到状态
          activity_list = []
          for activity in activities:
              has_checked_in = CheckInRecord.objects.filter(
                  activity=activity, 
                  user=user
              ).exists()
              
              activity_list.append({
                  'activity': activity,
                  'has_checked_in': has_checked_in,
                  'checkin_time': CheckInRecord.objects.filter(
                      activity=activity, user=user
                  ).first().checkin_time if has_checked_in else None
              })
          
          context['activities'] = activity_list
          context['current_time'] = now
          return context
  ```

- **签到API视图**:
  ```python
  class CheckInAPIView(LoginRequiredMixin, View):
      def post(self, request, activity_id):
          try:
              activity = Activity.objects.get(
                  id=activity_id,
                  is_active=True,
                  start_time__lte=timezone.now(),
                  end_time__gte=timezone.now()
              )
              
              # 检查用户是否允许参与
              if not ActivityParticipation.objects.filter(
                  activity=activity, user=request.user, can_participate=True
              ).exists():
                  return JsonResponse({'success': False, 'error': '您无权参与此活动'})
              
              # 检查是否已签到
              if CheckInRecord.objects.filter(activity=activity, user=request.user).exists():
                  return JsonResponse({'success': False, 'error': '您已签到过此活动'})
              
              # 创建签到记录
              CheckInRecord.objects.create(
                  activity=activity,
                  user=request.user,
                  ip_address=self.get_client_ip(request),
                  user_agent=request.META.get('HTTP_USER_AGENT', '')
              )
              
              return JsonResponse({'success': True, 'message': '签到成功'})
              
          except Activity.DoesNotExist:
              return JsonResponse({'success': False, 'error': '活动不存在或已结束'})
      
      def get_client_ip(self, request):
          x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
          if x_forwarded_for:
              ip = x_forwarded_for.split(',')[0]
          else:
              ip = request.META.get('REMOTE_ADDR')
          return ip
  ```

### 4. 管理系统
**应用**: `management`
- **管理员仪表板**:
  ```python
  class ManagementDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
      template_name = 'management/dashboard.html'
      
      def test_func(self):
          return self.request.user.is_admin or self.request.user.is_superuser
      
      def handle_no_permission(self):
          messages.error(self.request, '您没有权限访问管理页面')
          return redirect('checkin:dashboard')
  ```

- **用户批量创建视图**:
  ```python
  class BulkUserCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
      template_name = 'management/bulk_user_create.html'
      
      def test_func(self):
          return self.request.user.is_admin
      
      def get(self, request):
          return render(request, self.template_name)
      
      def post(self, request):
          # 处理CSV或Excel文件上传
          file = request.FILES.get('user_file')
          student_ids = request.POST.get('student_ids', '').split()
          
          # 生成随机密码函数
          def generate_random_password():
              length = 12
              chars = string.ascii_letters + string.digits + '!@#$%^&*'
              return ''.join(random.choice(chars) for _ in range(length))
          
          # 创建用户
          created_users = []
          for student_id in student_ids:
              if CustomUser.objects.filter(student_id=student_id).exists():
                  continue
                  
              password = generate_random_password()
              user = CustomUser.objects.create_user(
                  student_id=student_id,
                  password=password
              )
              created_users.append({
                  'student_id': student_id,
                  'initial_password': password
              })
          
          # 导出到Excel
          if created_users:
              response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
              response['Content-Disposition'] = 'attachment; filename="users_export.xlsx"'
              
              workbook = Workbook()
              worksheet = workbook.active
              worksheet.title = '用户列表'
              
              # 添加表头
              worksheet.append(['学号', '初始密码'])
              
              # 添加数据
              for user_data in created_users:
                  worksheet.append([user_data['student_id'], user_data['initial_password']])
              
              workbook.save(response)
              return response
          
          messages.success(request, f'成功创建 {len(created_users)} 个用户')
          return redirect('management:user_list')
  ```

- **活动管理视图**:
  ```python
  class ActivityCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
      model = Activity
      template_name = 'management/activity_form.html'
      fields = ['name', 'description', 'start_time', 'end_time']
      
      def test_func(self):
          return self.request.user.is_admin
      
      def form_valid(self, form):
          form.instance.created_by = self.request.user
          response = super().form_valid(form)
          
          # 处理参与用户选择
          participant_ids = self.request.POST.getlist('participants')
          for user_id in participant_ids:
              ActivityParticipation.objects.create(
                  activity=self.object,
                  user_id=user_id,
                  can_participate=True
              )
          
          messages.success(self.request, '活动创建成功')
          return response
  ```

- **签到统计与导出**:
  ```python
  class CheckInStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
      def test_func(self):
          return self.request.user.is_admin
      
      def get(self, request, activity_id):
          activity = get_object_or_404(Activity, id=activity_id)
          records = CheckInRecord.objects.filter(activity=activity).select_related('user')
          
          # 生成Excel报表
          response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
          response['Content-Disposition'] = f'attachment; filename="checkin_stats_{activity_id}.xlsx"'
          
          workbook = Workbook()
          worksheet = workbook.active
          worksheet.title = '签到统计'
          
          # 添加表头
          worksheet.append(['学号', '签到时间', 'IP地址'])
          
          # 添加数据
          for record in records:
              worksheet.append([
                  record.user.student_id,
                  record.checkin_time.strftime('%Y-%m-%d %H:%M:%S'),
                  record.ip_address
              ])
          
          workbook.save(response)
          return response
  ```

- **网站设置视图**:
  ```python
  class SiteSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
      model = SystemConfig
      template_name = 'management/site_settings.html'
      fields = ['site_title', 'site_logo', 'technician_contact']
      success_url = reverse_lazy('management:dashboard')
      
      def test_func(self):
          return self.request.user.is_admin
      
      def get_object(self):
          return SystemConfig.objects.first()
      
      def form_valid(self, form):
          messages.success(self.request, '网站设置已更新')
          return super().form_valid(form)
  ```

## 安全配置

### 1. Django安全设置
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# 密码哈希配置
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### 2. 自定义密码验证器
```python
class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise ValidationError('密码必须包含至少一个特殊字符')
    
    def get_help_text(self):
        return '密码必须包含至少一个特殊字符'
```

## 中间件与权限控制

### 1. 安装检测中间件
```python
class InstallationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 排除安装相关的URL
        if request.path.startswith('/install/') or request.path.startswith('/static/'):
            return self.get_response(request)
        
        # 检查系统是否已安装
        try:
            if not SystemConfig.objects.filter(installed=True).exists():
                return redirect('installation:welcome')
        except (OperationalError, ProgrammingError):
            # 数据库未初始化
            return redirect('installation:welcome')
        
        return self.get_response(request)
```

### 2. 管理员权限装饰器
```python
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authentication:login')
        if not (request.user.is_admin or request.user.is_superuser):
            messages.error(request, '您没有权限访问此页面')
            return redirect('checkin:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
```

## URL路由配置

### 主URL配置
```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('install/', include('apps.installation.urls')),
    path('auth/', include('apps.authentication.urls')),
    path('checkin/', include('apps.checkin.urls')),
    path('manage/', include('apps.management.urls')),
    path('', RedirectView.as_view(pattern_name='checkin:dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 认证URL配置
```python
# authentication/urls.py
from django.urls import path
from .views import (
    CustomLoginView, 
    CustomLogoutView,
    RequiredPasswordChangeView,
    PasswordResetView
)

app_name = 'authentication'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password-change-required/', RequiredPasswordChangeView.as_view(), name='password_change_required'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
]
```

## 模板设计

**注：Bootstrap 5 开发环境下使用本地 assets/css/ 和 assets/js 中的，生产环境使用 jsdelivr**

### 基础模板
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ config.site_title|default:"签到系统" }}{% endblock %}</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- 自定义CSS -->
    <link href="{% static 'css/style.css' %}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'checkin:dashboard' %}">
                {% if config.site_logo %}
                    <img src="{{ config.site_logo.url }}" alt="Logo" height="30" class="me-2">
                {% endif %}
                {{ config.site_title|default:"签到系统" }}
            </a>
            
            {% if user.is_authenticated %}
            <div class="navbar-nav ms-auto">
                <span class="nav-item nav-link text-white">
                    学号: {{ user.student_id }}
                </span>
                <a class="nav-item nav-link text-white" href="{% url 'authentication:logout' %}">
                    退出登录
                </a>
            </div>
            {% endif %}
        </div>
    </nav>
    
    <!-- 主内容区 -->
    <main class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    <!-- 页脚 -->
    <footer class="mt-5 py-3 bg-light">
        <div class="container text-center">
            <p class="mb-0">
                技术支持: {{ config.technician_contact|default:"请联系管理员" }}
            </p>
        </div>
    </footer>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- 自定义JS -->
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## 部署配置

**注：现有配置文件为 Django 自动生成（单 NeoSign/settings.py），如需调整（进行分块），请确保 Django 能识别**

### 生产环境设置
```python
# settings/production.py
import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# 静态文件配置
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# 请参考现有
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 媒体文件配置
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# 请参考现有
MEDIA_URL = '/media/'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django_error.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## 开发与部署步骤

### 1. 初始化项目

使用 uv 包管理工具

```bash
# 创建项目(已完成)
# django-admin startproject sign_system .

# 创建应用
uv run manage.py startapp core
uv run manage.py startapp installation
uv run manage.py startapp authentication
# uv run manage.py startapp checkin 已完成
uv run manage.py startapp management

# 创建自定义用户模型
uv run manage.py makemigrations core
uv run manage.py migrate

# 收集静态文件
uv run manage.py collectstatic
```

### 2. 安装依赖
使用 uv 包管理工具自动完成，包含以下库
```txt
"django>=6.0",
"dotenv>=0.9.9",
"gunicorn>=23.0.0",
"openpyxl>=3.1.5",
"pillow>=12.0.0",
"psycopg2>=2.9.11",
```

### 3. 环境变量配置
```bash
# .env
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_NAME=sign_system
DB_USER=db_user
DB_PASSWORD=secure-password-here
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=.your-domain.com
```

## 验收标准

1. 完整的安装向导，支持数据库配置和超级用户创建
2. 用户登录系统，支持10位数字学号和强密码验证
3. 首次登录强制修改密码功能
4. 签到功能，显示活动列表和签到状态
5. 管理员后台，包含用户管理、活动管理、签到统计
6. 批量用户创建和Excel导出功能
7. 网站设置管理（标题、logo、联系方式）
8. 完整的安全防护（CSRF、XSS、SQL注入防护）
9. 响应式设计，支持移动端访问
10. 完整的错误处理和日志记录

## 扩展功能建议

1. **QR码签到**: 为每个活动生成唯一的QR码
2. **邮件通知**: 发送密码重置邮件、活动提醒
3. **微信小程序**: 开发配套的微信小程序签到端
4. **数据可视化**: 使用Chart.js展示签到统计数据
5. **API接口**: 提供RESTful API供第三方系统集成
6. **多语言支持**: 添加中英文界面切换
7. **实时通知**: 使用WebSocket实现实时签到通知
8. **人脸识别**: 集成人脸识别签到（需要额外硬件支持）

这个Django实现方案充分利用了Django框架的内置功能，提供了完整的MVC架构、安全管理、表单验证和数据库ORM支持，相比原生PHP实现更加安全、可维护和可扩展。