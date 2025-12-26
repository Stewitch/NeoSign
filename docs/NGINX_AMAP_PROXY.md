# Nginx AMap Security Key Proxy Configuration

This document solves one problem: **Using AMap securityJsCode securely in production** without exposing it to the frontend.

Core Concept:

- The security key is stored only in Nginx configuration.
- The frontend only knows a `serviceHost`.
- All requests are proxied via `/_AMapService/` to `restapi.amap.com`, with Nginx appending the `jscode`.

---

## 1. Prerequisites

- An HTTPS site exposed via Nginx (e.g., `https://sign.example.com`).
- Obtained **JavaScript API Key** and **securityJsCode** from AMap Console.
- NeoSign backend supports `AMAP_PROXY_MODE` env var.

Enable proxy mode in production `.env`:

```env
AMAP_PROXY_MODE=nginx
```

---

## 2. Nginx Proxy Configuration

Add the AMap proxy block inside your site's `server { ... }` block:

```nginx
server {
    listen 443 ssl http2;
    server_name sign.example.com;

    # ... SSL and other config ...

    # AMap API Proxy
    # Proxy all AMap API requests via /_AMapService/
    location /_AMapService/ {
        # Append security key on server side (Only Nginx knows this)
        set $args "$args&jscode=YOUR_AMAP_SECURITY_KEY";

        proxy_pass https://restapi.amap.com/;
        proxy_ssl_server_name on;
        proxy_set_header Host restapi.amap.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Simple cache and CORS settings
        add_header Cache-Control "public, max-age=300";
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";

        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # Other Django / Static config omitted
}
```

Key Points:

- Replace `YOUR_AMAP_SECURITY_KEY` with your actual `securityJsCode`.
- The path prefix must be `/_AMapService/` (AMap requirement).
- `proxy_pass` must end with `/`: `https://restapi.amap.com/`.

---

## 3. Frontend / NeoSign Configuration

When `AMAP_PROXY_MODE=nginx` is set, the backend injects this into the frontend:

```js
window._AMapSecurityConfig = {
  serviceHost: "https://sign.example.com/_AMapService"
};
```

Checkpoints:

- `securityJsCode` field **should not** exist.
- AMap JS SDK will send requests to `https://sign.example.com/_AMapService/...`, which Nginx forwards to `restapi.amap.com`.

If you see this in console:

```js
window._AMapSecurityConfig
// { serviceHost: "https://sign.example.com/_AMapService" }
```

And Network requests go to `/_AMapService/`, the frontend config is correct.

---

## 4. Verification

1. Check and reload Nginx:
   ```bash
   nginx -t
   nginx -s reload
   ```
2. Open NeoSign, go to an activity with map.
3. Check Network tab in DevTools.
4. You should see requests to `/_AMapService/v3/...` returning 200 OK.
