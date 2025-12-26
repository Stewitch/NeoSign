# 配置指南

## 系统要求
- Python 3.12+
- PostgreSQL 14+ (已在 18 版本测试)
- 不需要 Node (静态资源已预打包)

## 环境变量
在项目根目录创建 `.env` 文件。本地开发配置：

```env
# 本地开发设置 (HTTP, 无 SSL 重定向)
DEBUG=True
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# 禁用 SSL 相关的重定向和 cookie 标志
SECURE_SSL_REDIRECT=False
CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False

# 数据库 (如果本地使用 Postgres，请调整)
DB_NAME=neosign
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

生产环境配置请参考 [DEPLOYMENT.zh.md](DEPLOYMENT.zh.md)。

## 本地开发
1. 安装 uv 并创建虚拟环境：
   ```bash
   # 安装 uv (如果未安装)
   pip install uv
   
   # 创建虚拟环境
   uv venv
   
   # 激活环境
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   
   # 安装依赖
   uv pip install -e .
   ```
2. 迁移数据库并创建管理员：
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py compilemessages -l en
   ```
3. 运行开发服务器：
   ```bash
   python manage.py runserver
   ```

### 局域网访问（手机同网络测试）
- 在所有网络接口上运行: `python manage.py runserver 0.0.0.0:8000`
- 找到局域网 IP（如 `192.168.1.20`），在手机上访问 `http://<LAN-IP>:8000`
- 更新环境变量: `ALLOWED_HOSTS=<LAN-IP>` 和 `CSRF_TRUSTED_ORIGINS=http://<LAN-IP>`
- 确保 Windows 防火墙允许端口 `8000` 的专用网络入站连接
- 本地使用 HTTP；禁用 `SECURE_SSL_REDIRECT` 避免 HTTPS 重定向

### HTTPS 开发环境（相机/地理位置 API）
现代浏览器要求使用 HTTPS（或 localhost）才能访问相机和精确地理位置。局域网移动端测试：

1. 安装 mkcert（可信本地 CA）
   - Windows: `choco install mkcert` 或从 releases 下载
   - macOS: `brew install mkcert`
   - Linux: 参考 mkcert 文档
   - 信任本地 CA: `mkcert -install`
2. 生成证书
   - 找到局域网 IP（如 `192.168.1.20`）
   - 运行: `mkcert localhost 127.0.0.1 <your-LAN-IP>`
   - 生成 `localhost+2.pem` 和 `localhost+2-key.pem`（文件名可能不同）
3. 启动 HTTPS 开发服务器
```
python manage.py runserver_plus 0.0.0.0:8443 \
  --cert-file=./localhost+2.pem \
  --key-file=./localhost+2-key.pem
```
   需要 `django-extensions` 和 `Werkzeug`（已包含在依赖中）
4. 更新 .env 配置
```
ALLOWED_HOSTS=localhost,127.0.0.1,<your-LAN-IP>
CSRF_TRUSTED_ORIGINS=https://localhost,https://127.0.0.1,https://<your-LAN-IP>
SECURE_SSL_REDIRECT=False
```
5. 从移动设备访问
   - 浏览器打开 `https://<your-LAN-IP>:8443`
   - 提示时信任证书（需在移动设备上安装 mkcert CA 以完全信任）
   - 相机和地理位置 API 将正常工作

**替代方案:** 使用 ngrok 或类似的隧道服务，无需本地证书管理。

## 快速启动脚本（可选）
用于快速迭代开发的脚本示例，会自动执行迁移、编译消息并启动服务器：

**PowerShell（启用 HTTPS）:**
```powershell
.\.venv\Scripts\activate.ps1
python .\manage.py makemigrations
python .\manage.py migrate
python .\manage.py compilemessages -l en
python .\manage.py runserver_plus 0.0.0.0:8443 --cert-file=./localhost+2.pem --key-file=./localhost+2-key.pem
```

**PowerShell（仅 HTTP）:**
```powershell
.\.venv\Scripts\activate.ps1
python .\manage.py makemigrations
python .\manage.py migrate
python .\manage.py compilemessages -l en
python .\manage.py runserver 0.0.0.0:8000
```

## 常用命令
- 运行测试: `python manage.py test`
- 代码检查（如已配置）: `ruff check .`
- Django Shell: `python manage.py shell`
