# NeoSign
[中文文档](README.CN.md)

A sign-in system built with Django 6 and PostgreSQL 18.

## Features
- Check-in activities with QR and/or geofence
- Admin dashboard for activities, participants, and exports
- User bulk import/reset with generated passwords
- i18n: zh-Hans and en-US

## Requirements
- Python 3.12+
- PostgreSQL 14+ (tested with 18)
- Node is **not** required (static assets are pre-bundled)

## Environment variables (.env)
Create a `.env` at project root:

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
# Optional when behind reverse proxy
# SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

## Local setup (development)
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

## Production deployment checklist
1) Set env vars: `DEBUG=False`, strong `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, secure cookie flags.
2) Install dependencies: `pip install -e .` (in a virtualenv).
3) Database: ensure PostgreSQL reachable; run `python manage.py migrate`.
4) Static files: enable manifest storage and compression (recommended):
	- In settings, set `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"` and add `whitenoise.middleware.WhiteNoiseMiddleware` after `SecurityMiddleware`.
	- Run `python manage.py collectstatic`.
5) Translations: `python manage.py compilemessages -l en` (and other locales as needed).
6) Create admin: `python manage.py createsuperuser`.
7) Run app behind a WSGI/ASGI server (gunicorn/uvicorn) with a reverse proxy for TLS; serve `/media` and `/static` either via proxy or WhiteNoise.
8) Verify deployment with `python manage.py check --deploy`.

## Database backup/restore
- Backup: `pg_dump -Fc -f neosign.dump neosign`
- Restore: `pg_restore -d neosign neosign.dump`

## Useful commands
- Run tests: `python manage.py test`
- Lint (if configured): `ruff check .`
- Shell: `python manage.py shell`

## Folder layout
- `NeoSign/` Django project settings and URLs
- `core/` shared models and middleware
- `authentication/` auth views and forms
- `management/` admin dashboard
- `checkin/` participant-side views and API
- `installation/` first-run setup
- `templates/` HTML templates
- `assets/` static files source (collected to `staticfiles/`)
- `locale/` translations
