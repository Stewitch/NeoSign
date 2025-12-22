# NeoSign
[English](README.md)

一个基于 Django 6 和 PostgreSQL 18 的签到系统。

## 功能特性
- 支持二维码与地理围栏签到
- 后台管理活动、参与者、导出
- 用户批量导入/重置并生成初始密码
- 国际化：简体中文与英文

## 环境要求
- Python 3.12+
- PostgreSQL 14+（测试使用 18）
- 无需 Node（静态资源已打包）

## 环境变量 (.env)
在项目根目录创建 `.env`：
```
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=example.com
CSRF_TRUSTED_ORIGINS=https://example.com
DB_NAME=neosign
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
# 反向代理场景可选
# SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

## 开发环境搭建
```
python -m venv .venv
.venv/Scripts/activate
pip install -U pip
pip install -e .
python manage.py migrate
python manage.py createsuperuser
python manage.py compilemessages -l en
python manage.py runserver
```

## 生产部署清单
1) 设置环境变量：`DEBUG=False`、强随机 `SECRET_KEY`、`ALLOWED_HOSTS`、`CSRF_TRUSTED_ORIGINS`、安全 Cookie 相关标志。
2) 安装依赖：在虚拟环境里执行 `pip install -e .`。
3) 数据库：确认 PostgreSQL 可访问，执行 `python manage.py migrate`。
4) 静态文件：推荐开启指纹与压缩。
   - settings 中设置 `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"`，并在 `SecurityMiddleware` 之后加入 `whitenoise.middleware.WhiteNoiseMiddleware`。
   - 运行 `python manage.py collectstatic`。
5) 翻译：`python manage.py compilemessages -l en`（如有其他语言一并编译）。
6) 创建管理员：`python manage.py createsuperuser`。
7) 运行：使用 WSGI/ASGI 服务器（gunicorn/uvicorn），前置反向代理做 TLS；`/media`、`/static` 由代理或 WhiteNoise 提供。
8) 检查：`python manage.py check --deploy`。

## 数据库备份/恢复
- 备份：`pg_dump -Fc -f neosign.dump neosign`
- 恢复：`pg_restore -d neosign neosign.dump`

## 常用命令
- 运行测试：`python manage.py test`
- Lint（若已配置）：`ruff check .`
- 交互 Shell：`python manage.py shell`

## 目录结构
- `NeoSign/` 项目配置与路由
- `core/` 公共模型与中间件
- `authentication/` 登录与改密
- `management/` 后台管理
- `checkin/` 参与者视图与 API
- `installation/` 首次运行安装
- `templates/` 模板
- `assets/` 静态源文件（收集到 `staticfiles/`）
- `locale/` 翻译
