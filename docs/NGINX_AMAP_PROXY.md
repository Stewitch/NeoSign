# Nginx 高德地图安全密钥代理配置

## 概述

在生产环境中，为了避免将高德地图的安全密钥（`securityJsCode`）直接暴露在前端代码中，NeoSign 支持通过 Nginx 反向代理的方式转发安全密钥。

## 配置模式

NeoSign 支持两种安全密钥分发模式，通过环境变量 `AMAP_PROXY_MODE` 控制：

- **`frontend`**（默认）：安全密钥直接在模板渲染时输出到前端 JavaScript，简单但安全性较低
- **`nginx`**（推荐生产环境）：安全密钥仅存储在后端，前端通过 Django API 端点获取，该端点需配置 Nginx 反向代理，由 Nginx 直接返回密钥，避免请求到达 Django

## 配置步骤

### 1. 设置环境变量

在生产环境的 `.env` 文件中添加：

```env
AMAP_PROXY_MODE=nginx
```

### 2. 配置 Nginx

在 Nginx 配置文件中添加以下配置段（通常在 `server` 块内）：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... 其他 SSL 配置 ...
    
    # 高德地图安全密钥代理
    # 直接返回 JSON，不转发到后端 Django
    location = /api/amap-security/ {
        default_type application/json;
        add_header Cache-Control "public, max-age=3600";
        add_header Access-Control-Allow-Origin *;
        
        # 替换下面的 YOUR_AMAP_SECURITY_KEY 为实际的安全密钥
        return 200 '{"securityJsCode":"YOUR_AMAP_SECURITY_KEY"}';
    }
    
    # Django 应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件代理
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /path/to/your/project/media/;
        expires 7d;
    }
}
```

**重要**：将 `YOUR_AMAP_SECURITY_KEY` 替换为在高德地图开放平台获取的实际安全密钥。

### 3. 验证配置

1. 检查 Nginx 配置语法：
   ```bash
   sudo nginx -t
   ```

2. 重载 Nginx：
   ```bash
   sudo nginx -s reload
   ```

3. 测试代理端点：
   ```bash
   curl https://your-domain.com/api/amap-security/
   ```
   
   应该返回：
   ```json
   {"securityJsCode":"YOUR_AMAP_SECURITY_KEY"}
   ```

4. 访问 NeoSign 应用，查看浏览器控制台，确认高德地图正常加载且无安全密钥相关错误。

## 工作原理

### Nginx 代理模式（推荐）

```
┌─────────┐      1. 请求密钥      ┌───────┐
│ 浏览器  │ ──────────────────> │ Nginx │
│         │                      │       │
│         │ <──────────────────  │       │
└─────────┘   2. 直接返回 JSON    └───────┘
                                     │
                              (不转发到 Django)
```

优点：
- 安全密钥不出现在前端代码中
- 请求不经过 Django，性能更好
- 便于缓存，减少后端压力

### Frontend 模式（默认）

```
┌─────────┐      1. 访问页面      ┌─────────┐
│ 浏览器  │ ──────────────────> │ Django  │
│         │                      │         │
│         │ <──────────────────  │         │
└─────────┘   2. HTML 中包含密钥  └─────────┘
              window._AMapSecurityConfig = {...}
```

缺点：
- 安全密钥暴露在 HTML 源码中
- 任何人都可以查看和复用

## 故障排查

### 问题：访问 `/api/amap-security/` 返回 403

**原因**：环境变量 `AMAP_PROXY_MODE` 未设置为 `nginx`。

**解决**：
1. 确认 `.env` 文件中有 `AMAP_PROXY_MODE=nginx`
2. 重启 Django 应用

### 问题：地图加载失败，控制台显示安全密钥错误

**可能原因**：
1. Nginx 配置中的安全密钥错误
2. Nginx 未正确重载

**解决**：
1. 检查 Nginx 配置中的 `securityJsCode` 值是否正确
2. 确认 Nginx 已重载：`sudo nginx -s reload`
3. 清除浏览器缓存

### 问题：`/api/amap-security/` 返回 Django 错误页面

**原因**：Nginx 配置中该路由未正确拦截，请求被转发到了 Django。

**解决**：
1. 确认 Nginx 配置中 `location = /api/amap-security/` 位于 `location /` 之前
2. 使用 `location =` 精确匹配，而非 `location ~`

## 安全建议

1. **生产环境必须使用 HTTPS**：确保 SSL 证书有效，避免中间人攻击
2. **限制访问频率**：可在 Nginx 中配置 `limit_req` 防止密钥接口被滥用
3. **定期轮换密钥**：定期在高德地图平台重新生成安全密钥并更新 Nginx 配置
4. **监控异常访问**：通过 Nginx 日志监控 `/api/amap-security/` 的访问频率和来源

## 参考资料

- [高德地图 Web 服务 API - 安全密钥说明](https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode)
- [Nginx 官方文档](https://nginx.org/en/docs/)
