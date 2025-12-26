# 生产环境部署

## 环境变量（生产环境）
创建生产环境的 `.env` 配置文件：

```env
# 核心配置
DEBUG=False
SECRET_KEY=change-me-to-a-strong-random-string
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

# HTTPS & 代理
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
USE_X_FORWARDED_HOST=True

# 数据库 (PostgreSQL)
DB_NAME=neosign
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432

# 地图安全配置 (高德地图)
# 设置为 'nginx' 通过 nginx 代理安全密钥（生产环境推荐）
# 设置为 'frontend' 直接发送密钥到前端（较简单但不够安全）
AMAP_PROXY_MODE=nginx
```

## 生产环境检查清单
1) 按上述配置设置环境变量: `DEBUG=False`、强 `SECRET_KEY`、`ALLOWED_HOSTS`、`CSRF_TRUSTED_ORIGINS`、安全 cookie 标志
2) 在虚拟环境中安装依赖: `pip install -e .`
3) 数据库: 确保 PostgreSQL 可访问；运行 `python manage.py migrate`
4) 静态文件: 启用清单存储和压缩（推荐）:
   - 在 settings 中设置 `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"` 并在 `SecurityMiddleware` 后添加 `whitenoise.middleware.WhiteNoiseMiddleware`
   - 运行 `python manage.py collectstatic`
5) 翻译: `python manage.py compilemessages -l en`（以及其他需要的语言）
6) 创建管理员: `python manage.py createsuperuser`
7) 在 WSGI/ASGI 服务器（gunicorn/uvicorn）后运行应用，配合反向代理处理 TLS；通过代理或 WhiteNoise 提供 `/media` 和 `/static`
8) 验证部署: `python manage.py check --deploy`

## 数据库备份/恢复
- 备份: `pg_dump -Fc -f neosign.dump neosign`
- 恢复: `pg_restore -d neosign neosign.dump`

## Nginx 配置示例
完整的 Nginx 配置，包含 HTTPS、安全头、高德地图代理和 Django 上游服务器：

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /path/to/ssl/fullchain.pem;
    ssl_certificate_key /path/to/ssl/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 日志配置
    access_log /var/log/nginx/neosign_access.log;
    error_log /var/log/nginx/neosign_error.log;
    
    client_max_body_size 20M;
    
    # 高德地图 API 代理（生产环境强烈推荐）
    location /_AMapService/ {
        # 在服务器端自动附加安全密钥（替换为实际密钥）
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
    
    # 静态文件服务
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
    
    # Django 应用代理
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

详细的高德地图代理配置请参考 [NGINX_AMAP_PROXY.md](NGINX_AMAP_PROXY.md)。

## 地图 SDK 集成
- 通用配置: [MAP_SDK_GUIDE.md](MAP_SDK_GUIDE.md)
- 高德地图快速开始: [AMAP_QUICK_START.md](AMAP_QUICK_START.md)
