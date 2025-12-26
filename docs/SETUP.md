# Setup

## Requirements
- Python 3.12+
- PostgreSQL 14+ (tested with 18)
- Node is not required (static assets are pre-bundled)

## Environment variables
Create a `.env` at project root. For local development:

```env
# Local development settings (HTTP, no SSL redirects)
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# Disable SSL-related redirects/cookie flags for local
SECURE_SSL_REDIRECT=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# Database (adjust if you use Postgres locally)
DB_NAME=neosign
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

For production settings, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Local development
1. Install uv and create venv:
   ```bash
   # Install uv (if not installed)
   # ref: https://docs.astral.sh/uv/getting-started/installation/
   pip install uv
   
   # Create virtualenv
   uv venv
   
   # Install dependencies
   uv sync
   ```
2. Migrate and create admin:
   ```bash
   uv run manage.py migrate
   uv run manage.py createsuperuser --username <4 ~ 23 length integer ID>
   uv run manage.py compilemessages -l en
   ```
3. Run server:
   ```bash
   uv run manage.py runserver
   ```

### LAN access (mobile on same network)
- Run dev server on all interfaces: `python manage.py runserver 0.0.0.0:8000`.
- Find your LAN IP (e.g., `192.168.1.20`) and open `http://<LAN-IP>:8000` on your phone.
- Update env for dev: `ALLOWED_HOSTS=<LAN-IP>` and `CSRF_TRUSTED_ORIGINS=http://<LAN-IP>`.
- Ensure Windows Firewall allows inbound on port `8000` for Private network.
- Use HTTP locally; disable `SECURE_SSL_REDIRECT` to avoid HTTPS redirects.

### HTTPS development (for camera/geolocation APIs)
Modern browsers require HTTPS (or localhost) for camera and precise geolocation access. For mobile testing over LAN:

1. Install mkcert (trusted local CA)
   - Windows: `choco install mkcert` or download from releases
   - macOS: `brew install mkcert`
   - Linux: follow mkcert docs
   - Trust the local CA: `mkcert -install`
2. Generate certificates
   - Find your LAN IP (e.g., `192.168.1.20`)
   - Run: `mkcert localhost 127.0.0.1 <your-LAN-IP>`
   - This creates `localhost+2.pem` and `localhost+2-key.pem` (filenames may vary)
3. Start HTTPS dev server
```
python manage.py runserver_plus 0.0.0.0:8443 \
  --cert-file=./localhost+2.pem \
  --key-file=./localhost+2-key.pem
```
   Requires `django-extensions` and `Werkzeug` (already in dependencies).
4. Update .env for HTTPS
```
ALLOWED_HOSTS=localhost,127.0.0.1,<your-LAN-IP>
CSRF_TRUSTED_ORIGINS=https://localhost,https://127.0.0.1,https://<your-LAN-IP>
SECURE_SSL_REDIRECT=False
```
5. Access from mobile
   - Browse to `https://<your-LAN-IP>:8443`
   - Trust the certificate when prompted (install mkcert CA on mobile for full trust)
   - Camera and geolocation APIs will now work

**Alternative:** Use ngrok or similar tunneling if you prefer not managing certificates locally.

## Quick start scripts (optional)
If you prefer a one-liner script for local development:

**PowerShell (HTTPS, assuming mkcert certificates are present):**
```powershell
uv run .\manage.py makemigrations
uv run .\manage.py migrate
uv run .\manage.py compilemessages -l en
uv run .\manage.py runserver_plus 0.0.0.0:8443 --cert-file=./localhost+2.pem --key-file=./localhost+2-key.pem
```

**PowerShell (HTTP only):**
```powershell
uv run .\manage.py makemigrations
uv run .\manage.py migrate
uv run .\manage.py compilemessages -l en
uv run .\manage.py runserver 0.0.0.0:8000
```

## Useful commands
- Run tests: `uv run manage.py test`
- Lint (if configured): `ruff check .`
- Shell: `uv run manage.py shell`
