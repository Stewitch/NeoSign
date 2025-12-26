# MkDocs 多语言文档配置说明

本项目使用 MkDocs Material 主题和 mkdocs-static-i18n 插件实现多语言文档支持。

## 文档结构

文档采用 **suffix** 结构（后缀模式）：
- 英文文档：`docs/index.md`, `docs/SETUP.md`, `docs/DEPLOYMENT.md`
- 中文文档：`docs/index.zh.md`, `docs/SETUP.zh.md`, `docs/DEPLOYMENT.zh.md`
- 共享文档（地图指南）：保持单一版本，两种语言共用

## 本地预览

安装依赖：
```bash
pip install mkdocs-material mkdocs-static-i18n
```

启动本地服务器：
```bash
mkdocs serve
```

访问 `http://127.0.0.1:8000` 查看文档，右上角可切换语言。

## 添加新语言

1. 在 `mkdocs.yml` 的 `plugins.i18n.languages` 中添加新语言配置
2. 创建对应后缀的文档文件（如 `.ja.md` 表示日文）
3. 更新 `nav_translations` 添加导航翻译

## 发布

GitHub Actions 自动构建和发布多语言站点到 GitHub Pages。
- 工作流配置: `.github/workflows/docs.yml`
- 主配置文件: `mkdocs.yml`

构建后的站点将包含：
- `/` - 英文版（默认）
- `/zh/` - 中文版
