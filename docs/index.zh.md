# NeoSign 文档

NeoSign 是一个基于 Django 的签到系统，支持二维码/地理围栏考勤、管理后台，以及可选的地图 SDK 集成（高德、腾讯、谷歌地图）。

## 快速导航
- 项目概览与配置: [SETUP.zh.md](SETUP.zh.md)
- 生产环境部署清单: [DEPLOYMENT.zh.md](DEPLOYMENT.zh.md)
- 地图 SDK 集成与高德地图相关说明:
  - [MAP_SDK_GUIDE.md](MAP_SDK_GUIDE.md)
  - [AMAP_QUICK_START.md](AMAP_QUICK_START.md)
  - [NGINX_AMAP_PROXY.md](NGINX_AMAP_PROXY.md)

## 文档结构
- 配置: 本地环境、局域网/移动端访问、HTTPS 开发环境、环境变量
- 部署: 生产环境加固、静态文件、TLS/反向代理配置、备份/恢复
- 地图指南: 如何配置高德/腾讯/谷歌地图，以及如何代理高德地图

## 发布文档站点
- 仓库包含 GitHub Pages 工作流 [.github/workflows/docs.yml](.github/workflows/docs.yml)，使用 MkDocs 构建。
- 在 GitHub Pages 设置中启用 "GitHub Actions" 来源，即可发布最新构建。
- 在 [mkdocs.yml](mkdocs.yml) 中自定义导航或元数据；内容位于 [docs/](docs/) 目录。
