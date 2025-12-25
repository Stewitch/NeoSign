# 地图 SDK 集成指南 / Map SDK Integration Guide

## 概述 / Overview

NeoSign 支持可选的地图 SDK 集成，用于可视化位置签到。系统支持三种地图提供商：

- **高德地图 (AMap)** - 推荐中国大陆用户
- **腾讯地图 (Tencent Maps)** - 适用中国大陆用户
- **Google Maps** - 适用国际用户

## 工作模式 / Working Modes

### 模式 A：无 SDK（基础模式）
- 使用浏览器地理位置 API 自动获取坐标
- 发起者点击"使用当前位置"自动填充经纬度
- 签到时自动计算距离判断是否在范围内
- **无需申请 API Key，开箱即用**

### 模式 B：集成 SDK（可视化模式）
- 在活动创建/编辑页面显示交互式地图
- 可视化范围圆圈，直观展示签到区域
- 点击地图标记中心位置
- 更精确的坐标选择体验
- **需要申请对应的 API Key**

---

## 申请 API Key / Apply for API Key

### 1. 高德地图 (AMap) - 推荐国内用户

**申请步骤：**
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并登录控制台
3. 创建应用 → 添加 Key
4. 服务平台选择：**Web 端 (JSAPI)**
5. 复制生成的 **Key**（应用 Key）
6. **重要：** 在 Key 管理页面找到并复制 **安全密钥 (securityJsCode)**

**配置示例：**
- 地图提供商：`amap` 或 `高德 (AMap)`
- Map API Key：`your-amap-key-here`（应用 Key）
- 地图安全密钥：`your-security-jscode-here`（安全密钥）

**注意事项：**
- **2021年12月02日后申请的 Key 必须配合安全密钥使用**
- 安全密钥在高德控制台的"应用管理 → Key 管理"中查看
- 本系统采用**明文方式**设置安全密钥（适合开发和中小型项目）
- 生产环境建议通过 Nginx 代理转发（见高德官方文档）

**官方文档：**
- [JavaScript API 文档](https://lbs.amap.com/api/jsapi-v2/summary)
- [Key 申请指南](https://lbs.amap.com/api/jsapi-v2/guide/abc/prepare)
- [安全密钥使用说明](https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode)

---

### 2. 腾讯地图 (Tencent Maps)

**申请步骤：**
1. 访问 [腾讯位置服务](https://lbs.qq.com/)
2. 注册并登录控制台
3. 我的应用 → 创建应用 → 添加 Key
4. 服务类型选择：**WebServiceAPI**
5. 复制生成的 **Key**

**配置示例：**
- 地图提供商：`tencent` 或 `腾讯 (QQ 地图)`
- Map API Key：`your-tencent-key-here`

**官方文档：**
- [JavaScript API GL 文档](https://lbs.qq.com/webApi/javascriptGL/glGuide/glBasic)
- [Key 申请指南](https://lbs.qq.com/dev/console/application/mine)

---

### 3. Google Maps

**申请步骤：**
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目
3. 启用 **Maps JavaScript API**
4. 凭据 → 创建凭据 → API 密钥
5. 设置应用限制（推荐 HTTP 引用站点限制）
6. 复制生成的 **API Key**

**配置示例：**
- 地图提供商：`google` 或 `Google Maps`
- Map API Key：`your-google-maps-key-here`

**官方文档：**
- [Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [Get API Key](https://developers.google.com/maps/documentation/javascript/get-api-key)

**注意：** Google Maps 在中国大陆可能受网络限制影响。

---

## 配置步骤 / Configuration Steps

1. **申请 API Key**
   - 根据上述指南从对应平台获取 Key

2. **配置系统**
   - 登录管理后台
   - 进入 **网站设置** 页面
   - 选择 **地图提供商**（AMap/Tencent/Google）
   - 填写 **地图 API Key**
   - **如果选择高德地图**，还需填写 **地图安全密钥**（securityJsCode）
   - 点击保存

3. **创建位置签到活动**
   - 新建活动 → 签到形式选择 **位置** 或 **位置 + 二维码**
   - 点击"使用当前位置"获取坐标
   - 若已配置 SDK，下方会显示可视化地图
   - 点击地图标记中心位置，调整范围半径
   - 保存活动

4. **测试签到**
   - 用户签到时系统会自动获取位置并判断是否在范围内
   - 如需调试，建议在 HTTPS 环境测试（浏览器安全要求）

---

## 费用说明 / Pricing

- **高德地图**: 个人开发者配额充足，基本免费
- **腾讯地图**: 每日免费配额足够小型应用
- **Google Maps**: 每月 $200 免费额度，超出按量计费

建议根据实际用户量评估选择合适的提供商。

---

## 故障排查 / Troubleshooting

**问题：地图不显示**
- 检查 API Key 是否正确填写
- **高德地图用户**：确认安全密钥（securityJsCode）已正确填写
  - **生产环境推荐**：使用 Nginx 代理模式，参见 [Nginx 高德地图安全密钥代理配置](NGINX_AMAP_PROXY.md)
- 检查 Key 的服务类型是否选择了 Web/JSAPI
- 打开浏览器开发者工具查看控制台错误
- 常见错误：`INVALID_USER_SCODE` 表示安全密钥错误或缺失

**问题：签到失败提示"不在范围内"**
- 确认活动设置的中心坐标准确
- 检查范围半径设置是否合理
- 在 HTTPS 环境下测试，确保浏览器能获取精确位置

**问题：摄像头/位置权限被拒**
- 必须使用 HTTPS 或 localhost 访问
- 检查浏览器权限设置
- 参考 README 中的 HTTPS 开发环境配置

---

## 安全建议 / Security Recommendations

- 不要在公开代码库中提交 API Key
- 为 API Key 设置 **域名白名单** 或 **IP 限制**
- 定期检查 Key 使用量，防止滥用
- 生产环境使用 HTTPS，避免 Key 泄露

---

## 更多帮助 / More Help

如需进一步帮助，请参考：
- [NeoSign README](../README.md)
- 各地图平台官方文档（见上方链接）
- 提交 Issue 到项目仓库
