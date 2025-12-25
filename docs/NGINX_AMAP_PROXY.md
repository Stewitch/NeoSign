# Nginx 高德地图安全密钥代理配置

> ⚠️ **安全警告**：本文档描述了正确且安全的高德地图安全密钥配置方式。**绝不要**将安全密钥暴露给前端或创建返回明文密钥的 API 端点！

## 概述

在生产环境中，**高德地图的安全密钥（`securityJsCode`）必须严格保密**，绝不能暴露在前端代码或网络传输中。NeoSign 通过 Nginx 服务器端代理实现安全的密钥管理：

- **密钥存储**：安全密钥只存储在 Nginx 配置文件中
- **自动附加**：Nginx 在转发 AMAP API 请求时自动附加 `jscode` 参数
- **前端隔离**：前端代码永远无法访问安全密钥
- **安全保障**：攻击者无法从前端代码、网络请求或 API 端点获取密钥

## 配置模式

NeoSign 支持两种模式，通过环境变量 `AMAP_PROXY_MODE` 控制：

- **`frontend`**（默认，⚠️ 不推荐）：安全密钥直接渲染到前端 JavaScript，**存在严重安全风险**
- **`nginx`**（✅ 强烈推荐生产环境）：安全密钥只存在于 Nginx 配置中，通过服务器端代理自动附加，**完全安全**

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
    
    # 高德地图 API 代理（关键配置）
    # 将所有 AMAP API 请求代理到高德服务器，并在服务器端自动附加安全密钥
    # _AMapService 是高德要求的固定前缀，不可修改
    location /_AMapService/ {
        # 在请求参数中自动附加安全密钥（安全密钥永不暴露给前端）
        set $args "$args&jscode=YOUR_AMAP_SECURITY_KEY";
        
        # 转发到高德服务器
        proxy_pass https://restapi.amap.com/;
        proxy_ssl_server_name on;
        proxy_set_header Host restapi.amap.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 缓存配置
        add_header Cache-Control "public, max-age=300";
        
        # CORS 配置
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";
        
        # 处理 OPTIONS 预检请求
        if ($request_method = OPTIONS) {
            return 204;
        }
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

**重要说明**：
- 将 `YOUR_AMAP_SECURITY_KEY` 替换为在高德地图开放平台获取的实际安全密钥
- `_AMapService` 是高德地图要求的固定前缀，**不能省略或修改**
- **关键**：使用 `set $args "$args&jscode=YOUR_AMAP_SECURITY_KEY";` 在 Nginx 服务器端自动附加安全密钥
- **安全密钥永远不会暴露给前端**，只在 Nginx → AMAP 的服务器端通信中使用
- 前端只需要设置 `serviceHost`，无需获取或设置 `securityJsCode`

### 3. 验证配置

1. 检查 Nginx 配置语法：
   ```bash
   sudo nginx -t
   ```

2. 重载 Nginx：
   ```bash
   sudo nginx -s reload
   ```

3. 测试 API 代理端点（例如测试地理编码）：
   ```bash
   curl 'https://your-domain.com/_AMapService/v3/geocode/geo?address=北京市朝阳区阜通东大街6号&key=YOUR_API_KEY'
   ```
   
   应该返回高德地图的 JSON 响应（包含经纬度等信息）
   
   **注意**：URL 中不需要包含 `jscode` 参数，Nginx 会自动附加

4. 访问 NeoSign 应用，打开浏览器开发者工具（F12）：
   - 在 "Network" 选项卡中，过滤 `_AMapService`，确认 AMAP API 请求通过你的域名代理
   - 在 "Console" 中运行 `window._AMapSecurityConfig`，应显示**只有** `serviceHost` 属性：
     ```javascript
     { serviceHost: "https://your-domain.com/_AMapService" }
     ```
   - **重要安全检查**：确认没有 `securityJsCode` 属性！如果有，说明存在安全漏洞！
   - 确认地图正常加载且无 `INVALID_USER_DOMAIN` 错误

## 工作原理

### Nginx 代理模式（推荐）

**AMAP API 请求代理**（解决 INVALID_USER_DOMAIN 的关键）：
```
┌─────────┐  1. API 请求（不含密钥）  ┌───────┐  2. 自动附加 jscode     ┌──────────┐
│ 浏览器  │ ─────────────────────> │ Nginx │ ────────────────────> │ 高德服务器│
│         │  /_AMapService/v3/...  │       │  /v3/...?key=X&jscode=Y│          │
│         │                         │       │                        │          │
│         │ <───────────────────── │       │ <─────────────────────│          │
└─────────┘  4. 返回结果            └───────┘  3. 获取结果           └──────────┘
    ↑                                 ↑                                   ↑
    └─ 前端永远看不到安全密钥         └─ 在服务器端附加密钥           检查来源域名 OK
```

**关键安全优势**：
- **安全密钥永远不暴露给前端**：密钥只存在于 Nginx 配置中
- **前端只设置 serviceHost**：`window._AMapSecurityConfig = { serviceHost: "..." }`
- **Nginx 自动附加密钥**：通过 `set $args "$args&jscode=密钥";` 在服务器端附加
- **域名验证通过**：所有请求的 Referer 都是你的域名（在白名单内）
- **无安全漏洞**：攻击者无法从前端代码或 API 端点获取安全密钥

### Frontend 模式（默认，⚠️ 不推荐，存在安全风险）

```
┌─────────┐      1. 访问页面      ┌─────────┐
│ 浏览器  │ ──────────────────> │ Django  │
│         │                      │         │
│         │ <──────────────────  │         │
└─────────┘   2. HTML 中包含密钥  └─────────┘
              window._AMapSecurityConfig = {securityJsCode: "密钥"}
```

**严重缺点**：
- ❌ **安全密钥暴露在前端代码中**：任何人都可以查看页面源码获取
- ❌ **密钥可被滥用**：攻击者可复用你的密钥发起大量请求
- ❌ **可能导致额外费用**：恶意使用会消耗你的 AMAP API 配额
- ❌ **违反安全最佳实践**：敏感凭证不应暴露给客户端

**⚠️ 强烈建议生产环境使用 Nginx 代理模式！**

## 故障排查

### ⚠️ 安全问题：检查是否存在密钥泄露

**检查方法**：
1. 打开浏览器开发者工具 (F12) → Console
2. 运行 `window._AMapSecurityConfig`
3. 如果看到 `securityJsCode` 属性，说明**存在安全漏洞**！

**修复方法**：
1. 立即设置 `AMAP_PROXY_MODE=nginx` 并重启应用
2. 按本文档配置 Nginx 代理
3. 考虑在 AMAP 开放平台重新生成密钥（如果旧密钥已泄露）

### 问题：地图加载失败或控制台显示密钥错误

**可能原因**：
1. Nginx 配置中的安全密钥错误（检查 `set $args` 中的密钥）
2. Nginx 未正确重载（运行 `sudo nginx -s reload`）
3. 前端仍在尝试获取 `securityJsCode`（应只设置 `serviceHost`）

**解决**：
1. 检查 Nginx 配置中的 `securityJsCode` 值是否正确
2. 确认 Nginx 已重载：`sudo nginx -s reload`
3. 清除浏览器缓存

### 问题：`/api/amap-security/` 返回 Django 错误页面

**原因**：Nginx 配置中该路由未正确拦截，请求被转发到了 Django。

**解决**：
1. 确认 Nginx 配置中 `location = /api/amap-security/` 位于 `location /` 之前
2. 使用 `location =` 精确匹配，而非 `location ~`

### 问题：控制台报错 `INVALID_USER_DOMAIN`

**原因**：AMAP 服务器验证请求来源域名与在开放平台配置的域名不匹配。这个错误通常由以下原因引起：

1. **未配置 API 代理（最常见）**：如果只配置了安全密钥但没有配置 `/_AMapService/` 代理，AMAP 的 API 请求仍会直接发送到高德服务器，导致域名验证失败
2. **使用了错误的 API Key 或 Security Key**：确保前端加载的 key 与在 AMAP 开放平台注册的 key 一致
3. **域名白名单配置不完整**：AMAP 要求在开放平台明确配置允许的域名
4. **Referer/Origin 头被篡改**：在代理环境下，需要正确转发请求头
5. **密钥已过期或被禁用**：在 AMAP 开放平台检查密钥是否仍然有效
6. **安全密钥类型不匹配**：Web Service Key（用于服务器端）与 JavaScript API Key（用于前端）不能混用

**核心解决方案：配置完整的代理**

确保 Nginx 配置中包含 `/_AMapService/` 代理配置，**这是解决 INVALID_USER_DOMAIN 的关键！**

没有代理配置，所有 AMAP API 请求仍会直接发送到 `restapi.amap.com`，导致域名验证失败。

**诊断步骤**：

1. **检查前端是否正确配置了 serviceHost（且没有 securityJsCode）**
   - 打开浏览器开发者工具 (F12) → Console
   - 运行 `window._AMapSecurityConfig`
   - 应该看到**只有一个属性**的对象：
     ```javascript
     { serviceHost: "https://sign.stewitch.com/_AMapService" }
     ```
   - **安全检查**：如果看到 `securityJsCode` 属性，说明存在严重安全漏洞！

2. **检查 API 请求是否通过代理**
   - F12 → Network 选项卡
   - 过滤包含 `_AMapService` 的请求
   - 应该看到类似 `https://sign.stewitch.com/_AMapService/v3/geocode/geo?...` 的请求
   - 点击查看请求详情，确认 URL 参数中**没有** `jscode`（由 Nginx 自动附加）
   - 如果看不到 `_AMapService` 请求，说明前端未正确设置 serviceHost
   - 如果看到请求失败（404/502），说明 Nginx 代理配置有问题

3. **验证 Nginx 代理是否正确附加密钥**
   - 在服务器上查看 Nginx access.log
   - 找到转发到 `restapi.amap.com` 的请求
   - 确认请求 URL 中包含 `jscode` 参数
   - 或者手动测试（注意：这会在 Nginx 日志中暴露密钥，测试后应清除日志）：
     ```bash
     curl 'https://sign.stewitch.com/_AMapService/v3/config?key=YOUR_API_KEY'
     ```
   - 应该返回高德地图的正常响应（说明密钥已正确附加）

4. **检查 AMAP 开放平台的域名配置**
   - 登录 [高德开放平台](https://lbs.amap.com/)
   - 进入 "应用管理" → "我的应用"
   - 选中你的应用，查看 "应用 Key" 列表
   - 对于 JavaScript API Key，检查 "服务平台" 和 "域名白名单" 配置
   - 确保包含你的域名（如 `sign.stewitch.com` 或 `*.stewitch.com`）
   - 如果修改了白名单，需等待 5-10 分钟生效
   - **注意**：配置了完整代理后，域名白名单要求会降低，因为所有请求都通过你的服务器转发

5. **检查 Nginx 日志**
   - 查看 Nginx access.log 和 error.log
   - 搜索包含 `_AMapService` 的请求记录
   - 检查是否有代理错误或连接超时

**快速排查清单**：
- [ ] 确认 Nginx 配置中有 `location /_AMapService/` 且包含 `set $args "$args&jscode=...";`
- [ ] 确认前端 `window._AMapSecurityConfig` **只有** `serviceHost`，**没有** `securityJsCode`
- [ ] 在浏览器 Network 中看到 `/_AMapService/` 开头的 API 请求
- [ ] 手动 curl 测试 `/_AMapService/` 端点可以正常返回数据
- [ ] 确认在 AMAP 开放平台配置了域名白名单
- [ ] 确认使用的是 JavaScript API Key（而非 Web Service Key）
- [ ] 确认 API Key 的 "应用状态" 为 "正常"
- [ ] 清除浏览器缓存并硬刷新（Ctrl+Shift+R）
- [ ] 检查 Nginx 重载后配置是否生效（`sudo nginx -s reload`）

**常见配置错误**：
- ❌ 前端直接设置 `securityJsCode`（严重安全漏洞！）
- ❌ Nginx 配置中缺少 `set $args "$args&jscode=...";`
- ❌ `location /_AMapService/` 放在了 `location /` 之后（被覆盖）
- ❌ 前端未设置 `serviceHost` 或设置错误
- ❌ `proxy_pass` 后面缺少斜杠（应为 `https://restapi.amap.com/` 而非 `https://restapi.amap.com`）

## 安全建议

### 关键安全原则

1. **⚠️ 绝不暴露安全密钥给前端**
   - 安全密钥只应存在于服务器端配置（Nginx 配置文件）
   - 前端代码和 API 端点都不应返回 `securityJsCode`
   - 定期审计：检查 `window._AMapSecurityConfig` 不包含 `securityJsCode`

2. **生产环境必须使用 Nginx 代理模式**
   - 设置 `AMAP_PROXY_MODE=nginx`
   - 通过 `set $args` 在服务器端附加密钥
   - 禁用任何暴露密钥的前端逻辑

3. **生产环境必须使用 HTTPS**
   - 确保 SSL 证书有效，避免中间人攻击
   - 配置 HSTS 头强制 HTTPS 访问

4. **限制 API 访问频率**
   - 在 Nginx 中配置 `limit_req` 防止代理接口被滥用：
     ```nginx
     limit_req_zone $binary_remote_addr zone=amap:10m rate=10r/s;
     
     location /_AMapService/ {
         limit_req zone=amap burst=20 nodelay;
         # ... 其他配置
     }
     ```

5. **定期轮换密钥**
   - 定期在高德地图平台重新生成安全密钥
   - 更新 Nginx 配置并重载
   - 如果发现密钥泄露，立即重新生成

6. **监控异常访问**
   - 通过 Nginx 日志监控 `/_AMapService/` 的访问频率和来源
   - 设置告警：异常流量激增可能表示滥用
   - 定期审计访问日志

7. **最小权限原则**
   - 在 AMAP 开放平台只启用必需的服务
   - 设置合理的日配额限制
   - 配置 IP 白名单（如果可能）

### 迁移检查清单（从不安全配置升级）

如果你之前使用了不安全的配置，请按以下步骤修复：

- [ ] 在 AMAP 开放平台重新生成安全密钥（废弃旧密钥）
- [ ] 更新 Nginx 配置，使用 `set $args "$args&jscode=新密钥";`
- [ ] 移除前端代码中所有 `securityJsCode` 相关逻辑
- [ ] 确认 `window._AMapSecurityConfig` 只包含 `serviceHost`
- [ ] 设置 `AMAP_PROXY_MODE=nginx` 并重启应用
- [ ] 清除所有客户端缓存
- [ ] 验证地图功能正常工作
- [ ] 审计 Nginx 日志，确认没有异常访问

## 参考资料

- [高德地图 Web 服务 API - 安全密钥说明](https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode)
- [高德地图 - 代理服务器设置](https://lbs.amap.com/api/javascript-api-v2/guide/abc/proxy)
- [Nginx 官方文档](https://nginx.org/en/docs/)
- [Nginx 限流配置](http://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
