# Nginx 高德地图安全密钥代理配置

本文档只解决一件事：**在生产环境安全地使用高德 securityJsCode**，不把密钥丢到前端。

核心思路：

- 安全密钥只写在 Nginx 配置里；
- 前端只知道一个 `serviceHost`；
- 所有请求通过 `/_AMapService/` 代理到 `restapi.amap.com`，由 Nginx 自动拼上 `jscode`。

---

## 1. 环境准备

前提：

- 已有一个通过 Nginx 暴露的 HTTPS 站点（例如 `https://sign.example.com`）；
- 已在高德控制台申请 **JavaScript API Key** 和 **securityJsCode**；
- NeoSign 后端版本支持 `AMAP_PROXY_MODE` 环境变量。

在生产 `.env` 中开启代理模式：

```env
AMAP_PROXY_MODE=nginx
```

---

## 2. Nginx 代理配置

在对应站点的 `server { ... }` 内添加高德代理段：

```nginx
server {
    listen 443 ssl http2;
    server_name sign.example.com;

    # ... 证书与站点其他配置 ...

    # 高德地图 API 代理
    # 通过 /_AMapService/ 代理所有 AMAP API 请求
    location /_AMapService/ {
        # 在服务器端自动附加安全密钥（仅 Nginx 知道）
        set $args "$args&jscode=YOUR_AMAP_SECURITY_KEY";

        proxy_pass https://restapi.amap.com/;
        proxy_ssl_server_name on;
        proxy_set_header Host restapi.amap.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 简单缓存与 CORS 设置
        add_header Cache-Control "public, max-age=300";
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";

        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # 其余 Django / 静态资源配置略
}
```

要点：

- 将 `YOUR_AMAP_SECURITY_KEY` 替换为从高德平台拿到的 `securityJsCode`；
- 路径前缀必须是 `/_AMapService/`（高德官方要求）；
- `proxy_pass` 末尾要带 `/`：`https://restapi.amap.com/`。

---

## 3. 前端 / NeoSign 配置说明

后端在 `AMAP_PROXY_MODE=nginx` 时，会只向前端注入：

```js
window._AMapSecurityConfig = {
  serviceHost: "https://sign.example.com/_AMapService"
};
```

检查点：

- **不应该**存在 `securityJsCode` 字段；
- 高德 JS SDK 会把所有接口请求发到 `https://sign.example.com/_AMapService/...`，再由 Nginx 中转到 `restapi.amap.com`。

如果你在控制台看到：

```js
>> window._AMapSecurityConfig
{ serviceHost: "https://sign.example.com/_AMapService" }
```

且 Network 里请求走的是 `/_AMapService/`，说明前端侧配置是对的。

---

## 4. 验证配置

1. 检查并重载 Nginx：
   ```bash
   sudo nginx -t
   sudo nginx -s reload
   ```

2. 本地测试代理（示例）：
   ```bash
   curl 'https://sign.example.com/_AMapService/v3/geocode/geo?address=北京市朝阳区阜通东大街6号&key=YOUR_AMAP_JS_API_KEY'
   ```

   - 能返回正常 JSON 即说明代理和 `jscode` 附加正常。

3. 浏览器端检查：

   - 打开 NeoSign，F12 → Network，过滤 `_AMapService`：
     - 请求 URL 形如 `https://sign.example.com/_AMapService/v3/...`；
     - 请求查询参数中 **看不到** `jscode`（它只出现在 Nginx → 高德那一跳）。
   - F12 → Console：
     - 运行 `window._AMapSecurityConfig`，应只有 `serviceHost`，没有 `securityJsCode`。

---

## 5. 常见问题

### 5.1 地图不加载 / 控制台报密钥错误

排查顺序：

- 确认 `AMAP_PROXY_MODE=nginx` 已生效（重启后端）；
- 检查 Nginx 配置里的 `securityJsCode` 是否正确粘贴；
- 再次运行 `sudo nginx -t && sudo nginx -s reload`；
- 清理浏览器缓存，重新打开页面。

### 5.2 Console 报 `INVALID_USER_DOMAIN`

意味着 **高德认为请求来源域名不在白名单**，常见原因：

- 未使用 `/_AMapService/` 代理，前端直接请求 `restapi.amap.com`；
- 高德控制台中域名白名单未包含 `sign.example.com`；
- 使用了错误的 JS API Key（非当前应用的）。

建议：

- 确保前端所有调用都走 `serviceHost` 代理；
- 在高德控制台为该 JS API Key 配置正确的域名白名单；
- 等待白名单变更在高德侧生效（通常几分钟）。

### 5.3 仍然怀疑密钥泄露怎么办？

最直接的安全恢复流程：

- 在高德平台为该应用重新生成 `securityJsCode`；
- 更新 Nginx 里的密钥并重载；
- 确认前端不再出现 `securityJsCode` 字段；
- 如有需要，审计一段时间内 `/_AMapService/` 的访问日志。

---

## 6. 安全加固建议（可选）

根据业务规模，可以再做几步加强：

- **限流**：防止滥用代理接口：
  ```nginx
  limit_req_zone $binary_remote_addr zone=amap:10m rate=10r/s;

  location /_AMapService/ {
      limit_req zone=amap burst=20 nodelay;
      # 其他代理配置同上
  }
  ```

- **最小权限**：在高德控制台只启用实际用到的服务，并设置合理的日配额；
- **日志监控**：定期查看 `/_AMapService/` 访问情况，异常流量及时报警；
- **全站 HTTPS**：配合 HSTS，确保所有地图相关请求都在 TLS 下进行。

---

## 7. 参考链接

- 高德安全密钥与代理：

  - https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode
  - https://lbs.amap.com/api/javascript-api-v2/guide/abc/proxy
  
- Nginx 文档：

  - https://nginx.org/en/docs/
  - http://nginx.org/en/docs/http/ngx_http_limit_req_module.html
