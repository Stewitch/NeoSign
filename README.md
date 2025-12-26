# NeoSign
[中文 README](README.CN.md)

> [!WARNING]
> The project is still in the early development stage,
> there may be several issues, and version updates may be fast.

A Django 6 + PostgreSQL sign-in system for QR/geofence attendance with admin dashboards.

[Documentation site](https://stewitch.github.io/NeoSign)

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
1. Create a `.env` file at project root (see environment variables in [Setup guide](https://stewitch.github.io/NeoSign/SETUP)).
2. Install dependencies and bootstrap the database:
```bash
# Install uv
pip install uv

# Create and activate venv
uv venv
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
uv pip install -e .

# Setup DB
python manage.py migrate
python manage.py createsuperuser
python manage.py compilemessages -l en
```
3. Run dev server: `python manage.py runserver`

## Documentation
- Online docs: [Documentation site](https://stewitch.github.io/NeoSign)
- Setup & local/LAN/HTTPS dev: [Setup guide](https://stewitch.github.io/NeoSign/SETUP)
- Production deployment & backup/restore: [Deployment guide](https://stewitch.github.io/NeoSign/DEPLOYMENT)
- Map SDK integration:
  - [Map SDK integration guide](https://stewitch.github.io/NeoSign/MAP_SDK_GUIDE)
  - [AMap quick start](https://stewitch.github.io/NeoSign/AMAP_QUICK_START)
  - [Nginx AMap proxy configuration](https://stewitch.github.io/NeoSign/NGINX_AMAP_PROXY)

## License
NeoSign is under [Apache 2.0 LICENSE](LICENSE)
