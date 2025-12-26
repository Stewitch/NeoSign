# NeoSign
[中文文档](README.CN.md)

A Django 6 + PostgreSQL sign-in system for QR/geofence attendance with admin dashboards.

## Features
- QR/geofence check-ins with optional map SDKs (AMap/Tencent/Google)
- Admin dashboard for activities, participants, and exports
- Bulk user import/reset with generated passwords
- i18n for zh-Hans and en-US
- RSA-encrypted login password transport (frontend to backend)

## Requirements
- Python 3.12+
- PostgreSQL 14+ (tested with 18)

## Quickstart
1) Create a `.env` file at project root (see environment variables in [docs/SETUP.md](docs/SETUP.md)).
2) Install dependencies and bootstrap the database:
```
python -m venv .venv
.venv/Scripts/activate
pip install -U pip
pip install -e .
python manage.py migrate
python manage.py createsuperuser
python manage.py compilemessages -l en
```
3) Run dev server: `python manage.py runserver`

## Documentation
- Docs home: [docs/index.md](docs/index.md)
- Setup, LAN/HTTPS dev, env vars: [docs/SETUP.md](docs/SETUP.md)
- Production and backup/restore: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- Map SDK integration and AMap proxying:
  - [docs/MAP_SDK_GUIDE.md](docs/MAP_SDK_GUIDE.md)
  - [docs/AMAP_QUICK_START.md](docs/AMAP_QUICK_START.md)
  - [docs/NGINX_AMAP_PROXY.md](docs/NGINX_AMAP_PROXY.md)

The GitHub Pages workflow at [.github/workflows/docs.yml](.github/workflows/docs.yml) builds the MkDocs site defined in [mkdocs.yml](mkdocs.yml).

## License
[LICENSE](LICENSE)
