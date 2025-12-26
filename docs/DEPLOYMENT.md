# Deployment

## Environment variables (production)
Create a `.env` with production settings:

```env
# Core
DEBUG=False
SECRET_KEY=change-me-to-a-strong-random-string
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

# HTTPS & proxy
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
USE_X_FORWARDED_HOST=True

# Database (PostgreSQL)
DB_NAME=neosign
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432

# Map Security (AMap)
# Set to 'nginx' to proxy security key via nginx (recommended)
# Set to 'frontend' to send key directly to frontend (simpler but less secure)
AMAP_PROXY_MODE=nginx
```

## Production checklist
1. Set env vars as shown above: `DEBUG=False`, strong `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, secure cookie flags.
2. Install dependencies in a virtualenv: `uv pip install -e .` (ensure `uv` is installed).
3. Database: ensure PostgreSQL reachable; run `python manage.py migrate`.
4. Static files: enable manifest storage and compression (recommended):
    - In settings, set `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"` and add `whitenoise.middleware.WhiteNoiseMiddleware` after `SecurityMiddleware`.
    - Run `python manage.py collectstatic`.
5. Translations: `python manage.py compilemessages -l en` (and other locales as needed).
6. Create admin: `python manage.py createsuperuser`.
7. Run app behind a WSGI/ASGI server (gunicorn/uvicorn) with a reverse proxy for TLS; serve `/media` and `/static` either via proxy or WhiteNoise.
8. Verify deployment with `python manage.py check --deploy`.

## Database backup/restore
- Backup: `pg_dump -Fc -f neosign.dump neosign`
- Restore: `pg_restore -d neosign neosign.dump`

## Nginx configuration example
Complete Nginx config with HTTPS, security headers, AMap proxy, and Django upstream:

```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL cert config
    ssl_certificate /path/to/ssl/fullchain.pem;
    ssl_certificate_key /path/to/ssl/privkey.pem;
    
    # SSL security config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # logs
    access_log /var/log/nginx/neosign_access.log;
    error_log /var/log/nginx/neosign_error.log;
    
    client_max_body_size 20M;
    
    # AMap API Proxy (For production env)
    location /_AMapService/ {
        # Replace to your real security key
        set $args "$args&jscode=YOUR_AMAP_SECURITY_KEY";
        
        proxy_pass https://restapi.amap.com/;
        proxy_ssl_server_name on;
        proxy_set_header Host restapi.amap.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        add_header Cache-Control "public, max-age=300";
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";
        
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
    
    # Static files
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/your/project/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Django application proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        
        # WebSocket 支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Also see [NGINX_AMAP_PROXY.md](NGINX_AMAP_PROXY.md) for detailed AMap proxy setup.

## Map SDK integration
- General setup: [MAP_SDK_GUIDE.md](MAP_SDK_GUIDE.md)
- AMap quick start: [AMAP_QUICK_START.md](AMAP_QUICK_START.md)
