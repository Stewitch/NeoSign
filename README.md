# NeoSign
[中文文档](README.CN.md)

A sign-in system built with Django 6 and PostgreSQL 18.

## Features
- Check-in activities with QR and/or geofence
- Admin dashboard for activities, participants, and exports
- User bulk import/reset with generated passwords
- i18n: zh-Hans and en-US
- Optional map SDK integration for visual location picking (AMap, Tencent, Google Maps)
  - **See [Map SDK Integration Guide](docs/MAP_SDK_GUIDE.md) for setup**

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
# Map security (for AMap only)
AMAP_PROXY_MODE=nginx  # 'nginx' or 'frontend' (default)
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

### LAN access (mobile on same network)
- Run dev server on all interfaces: `python manage.py runserver 0.0.0.0:8000`.
- Find your LAN IP (e.g., `192.168.1.20`) and open `http://<LAN-IP>:8000` on your phone.
- Update env for dev: `ALLOWED_HOSTS=<LAN-IP>` and `CSRF_TRUSTED_ORIGINS=http://<LAN-IP>` (see `.env.local.example`).
- Ensure Windows Firewall allows inbound on port `8000` for Private network.
- Use HTTP locally; disable `SECURE_SSL_REDIRECT` to avoid HTTPS redirects.

### HTTPS development (for camera/geolocation APIs)
Modern browsers require HTTPS (or localhost) for camera and precise geolocation access. For mobile testing over LAN:

1. **Install mkcert** (trusted local CA)
   - Windows: `choco install mkcert` or download from [releases](https://github.com/FiloSottile/mkcert/releases)
   - macOS: `brew install mkcert`
   - Linux: Follow [mkcert docs](https://github.com/FiloSottile/mkcert)
   - Trust the local CA: `mkcert -install`

2. **Generate certificates**
   - Find your LAN IP (e.g., `192.168.1.20`)
   - Run: `mkcert localhost 127.0.0.1 <your-LAN-IP>`
   - This creates `localhost+2.pem` and `localhost+2-key.pem` (filenames may vary)

3. **Start HTTPS dev server**
   ```bash
   python manage.py runserver_plus 0.0.0.0:8443 \
     --cert-file=./localhost+2.pem \
     --key-file=./localhost+2-key.pem
   ```
   *(Requires `django-extensions` and `Werkzeug` - already in dependencies)*

4. **Update .env for HTTPS**
   ```
   ALLOWED_HOSTS=localhost,127.0.0.1,<your-LAN-IP>
   CSRF_TRUSTED_ORIGINS=https://localhost,https://127.0.0.1,https://<your-LAN-IP>
   SECURE_SSL_REDIRECT=False
   ```

5. **Access from mobile**
   - Browse to `https://<your-LAN-IP>:8443`
   - Trust the certificate when prompted (mkcert CA must be installed on mobile device for full trust)
   - Camera and geolocation APIs will now work

**Alternative: Use ngrok or similar tunneling** if you prefer not managing certificates locally.

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
	- See prod env template: `.env.production.example`
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
