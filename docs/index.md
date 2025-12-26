# NeoSign Documentation

NeoSign is a Django-based check-in system with QR/geofence attendance, admin dashboards, and optional map SDK integration (AMap, Tencent, Google Maps).

## Start here
- Project overview and setup: [SETUP.md](SETUP.md)
- Production deployment checklist: [DEPLOYMENT.md](DEPLOYMENT.md)
- Map SDK integration and AMap-specific notes:
  - [MAP_SDK_GUIDE.md](MAP_SDK_GUIDE.md)
  - [AMAP_QUICK_START.md](AMAP_QUICK_START.md)
  - [NGINX_AMAP_PROXY.md](NGINX_AMAP_PROXY.md)

## Documentation structure
- Setup: local environment, LAN/mobile access, HTTPS dev, and environment variables.
- Deployment: production hardening, static files, TLS/reverse proxy hints, and backup/restore.
- Map Guides: how to configure AMap/Tencent/Google Maps and proxy AMap when needed.

## Publishing this site
- The repository includes a GitHub Pages workflow at [.github/workflows/docs.yml](.github/workflows/docs.yml) that builds with MkDocs.
- Enable GitHub Pages with the "GitHub Actions" source and it will publish from the latest build artifact.
- Customize the nav or metadata in [mkdocs.yml](mkdocs.yml); content lives in [docs/](docs/).
