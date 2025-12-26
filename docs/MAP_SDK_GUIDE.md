# Map SDK Integration Guide

## Overview

NeoSign supports optional Map SDK integration for visual location check-ins. The system supports three map providers:

- **AMap (Gaode)** - Recommended for users in Mainland China.
- **Tencent Maps** - Suitable for users in Mainland China.
- **Google Maps** - Suitable for international users.

## Working Modes

### Mode A: No SDK (Basic Mode)
- Uses Browser Geolocation API to automatically fetch coordinates.
- The initiator clicks "Use Current Location" to auto-fill latitude and longitude.
- Check-in automatically calculates distance to verify if within range.
- **No API Key required, works out of the box.**

### Mode B: Integrated SDK (Visual Mode)
- Displays an interactive map on the activity creation/edit page.
- Visualizes the range circle to intuitively show the check-in area.
- Click on the map to mark the center position.
- More precise coordinate selection experience.
- **Requires applying for the corresponding API Key.**

---

## Apply for API Key

### 1. AMap (Gaode) - Recommended for China

**Steps:**
1. Visit [AMap Open Platform](https://lbs.amap.com/).
2. Register and log in to the console.
3. Create Application -> Add Key.
4. Service Platform: **Web (JSAPI)**.
5. Copy the generated **Key** (App Key).
6. **Important:** Find and copy the **Security Key (securityJsCode)** in the Key Management page.

**Configuration Example:**
- Map Provider: `amap` or `AMap (Gaode)`
- Map API Key: `your-amap-key-here` (App Key)
- Map Security Key: `your-security-jscode-here` (Security Key)

**Notes:**
- **Keys applied after Dec 02, 2021 must be used with a Security Key.**
- The Security Key is viewed in "Application Management -> Key Management" in the AMap console.
- This system uses **plaintext** setting for the Security Key (suitable for dev and small projects).
- For production, it is recommended to use Nginx proxy forwarding (see AMap official docs).

**Official Docs:**
- [JavaScript API Docs](https://lbs.amap.com/api/jsapi-v2/summary)
- [Key Application Guide](https://lbs.amap.com/api/jsapi-v2/guide/abc/prepare)
- [Security Key Usage](https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode)

---

### 2. Tencent Maps

**Steps:**
1. Visit [Tencent Location Service](https://lbs.qq.com/).
2. Register and log in to the console.
3. My Applications -> Create Application -> Add Key.
4. Service Type: **WebServiceAPI**.
5. Copy the generated **Key**.

**Configuration Example:**
- Map Provider: `tencent` or `Tencent (QQ Maps)`
- Map API Key: `your-tencent-key-here`

**Official Docs:**
- [JavaScript API GL Docs](https://lbs.qq.com/webApi/javascriptGL/glGuide/glBasic)
- [Key Application Guide](https://lbs.qq.com/dev/console/application/mine)

---

### 3. Google Maps

**Steps:**
1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Create Project.
3. Enable **Maps JavaScript API**.
4. Credentials -> Create Credentials -> API Key.
5. Set Application Restrictions (HTTP Referrer restriction recommended).
6. Copy the generated **API Key**.

**Configuration Example:**
- Map Provider: `google` or `Google Maps`
- Map API Key: `your-google-maps-key-here`

**Official Docs:**
- [Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [Get API Key](https://developers.google.com/maps/documentation/javascript/get-api-key)

**Note:** Google Maps may be restricted in Mainland China.

---

## Configuration Steps

1. **Apply for API Key**
   - Get the Key from the corresponding platform according to the guide above.

2. **Configure System**
   - Login to Admin Panel.
   - Go to **Site Settings** page.
   - Select **Map Provider** (AMap/Tencent/Google).
   - Fill in **Map API Key**.
   - **If AMap is selected**, also fill in **Map Security Key** (securityJsCode).
   - Click Save.

3. **Create Location Check-in Activity**
   - New Activity -> Check-in Type select **Location** or **Location + QR Code**.
   - Click "Use Current Location" to get coordinates.
   - If SDK is configured, a visual map will appear below.
   - Click on the map to mark the center, adjust range radius.
   - Save Activity.

4. **Test Check-in**
   - When user checks in, the system automatically gets location and verifies range.
   - For debugging, test in HTTPS environment (Browser security requirement).

---

## Pricing

- **AMap**: Individual developer quota is sufficient, basically free.
- **Tencent Maps**: Daily free quota is enough for small apps.
- **Google Maps**: $200 monthly free credit, pay-as-you-go beyond that.

It is recommended to choose the appropriate provider based on actual user volume.

---

## Troubleshooting

**Issue: Map does not show**
- Check if API Key is filled correctly.
- **AMap Users**: Confirm Security Key (securityJsCode) is filled correctly.
  - **Production Recommendation**: Use Nginx proxy mode, see [Nginx AMap Proxy Configuration](NGINX_AMAP_PROXY.md).
- Check if Key Service Type is Web/JSAPI.
- Open Browser DevTools to check Console errors.
- Common Error: `INVALID_USER_SCODE` means Security Key is wrong or missing.

**Issue: Check-in fails with "Not in range"**
- Confirm the activity center coordinates are accurate.
- Check if range radius is reasonable.
- Test in HTTPS environment to ensure browser can get precise location.

**Issue: Camera/Location permission denied**
- Must use HTTPS or localhost.
- Check browser permission settings.
- Refer to HTTPS development environment config in README.

---

## Security Recommendations

- Do not commit API Keys to public repositories.
- Set **Domain Whitelist** or **IP Restriction** for API Keys.
- Regularly check Key usage to prevent abuse.
- Use HTTPS in production to avoid Key leakage.

---

## More Help

For further assistance, please refer to:
- "Setup" and "Deployment" sections in the project documentation site.
- Official documentation of each map platform (links above).
- Submit an Issue on the code hosting platform.
