# NeoSign
[English README](README.md)

> [!WARNING]
> 该项目仍在早期开发阶段，可能存在若干问题，并且版本更新可能较快。

一个基于 Django 6 和 PostgreSQL 的签到系统，支持二维码/地理围栏考勤与管理后台。

[文档站](https://stewitch.github.io/NeoSign/zh/)

## 功能特性
- 支持二维码与地理围栏签到，可选集成地图 SDK（高德、腾讯、Google Maps）
- 后台管理活动、参与者、导出数据
- 用户批量导入/重置并生成初始密码
- 国际化：简体中文与英文
- RSA 加密登录密码传输（前端到后端）

## 环境要求
- Python 3.12+
- PostgreSQL 14+（已在 18 上测试）

## 快速开始
1. 在项目根目录创建 `.env` 文件（环境变量参考 [配置指南](https://stewitch.github.io/NeoSign/zh/SETUP)）。
2. 安装依赖并初始化数据库：
```bash
# 安装 uv
pip install uv

# 创建并激活虚拟环境
uv venv
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# 安装依赖
uv pip install -e .

# 初始化数据库
python manage.py migrate
python manage.py createsuperuser
python manage.py compilemessages -l en
```
3. 运行开发服务器：`python manage.py runserver`

## 文档
- 在线文档: [文档站](https://stewitch.github.io/NeoSign/zh/)
- 配置指南 (本地/局域网/HTTPS 开发): [配置指南](https://stewitch.github.io/NeoSign/zh/SETUP)
- 生产环境部署 & 备份/恢复: [部署指南](https://stewitch.github.io/NeoSign/zh/DEPLOYMENT)
- 地图 SDK 集成:
  - [地图 SDK 集成指南](https://stewitch.github.io/NeoSign/zh/MAP_SDK_GUIDE)
  - [高德地图快速上手](https://stewitch.github.io/NeoSign/zh/AMAP_QUICK_START)
  - [Nginx 高德地图代理配置](https://stewitch.github.io/NeoSign/zh/NGINX_AMAP_PROXY)

## 许可证
NeoSign 基于 [Apache 2.0 LICENSE](LICENSE) 许可证开源。
