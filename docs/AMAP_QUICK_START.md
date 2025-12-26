# AMap Quick Start Guide

This guide helps you quickly configure AMap (Gaode Map) for visual location check-ins in a local development environment.

**Note: This guide uses the insecure frontend embedding mode for the security key. Do not use this in a production environment.**

## Step 1: Apply for AMap Keys

1. **Register Account**

   - Visit [AMap Open Platform](https://lbs.amap.com/).
   - Register and complete developer verification (Individual developer is sufficient).

2. **Create Application**

   - Go to Console -> Application Management -> My Applications.
   - Click "Create New Application".
   - Fill in App Name (e.g., NeoSign).
   - App Type: Other.

3. **Add Key**

   - Under the created app, click "Add".
   - Key Name: Any (e.g., Web).
   - Service Platform: **Web (JS API)**.
   - After submission, you will get:
     -  **App Key** (alphanumeric string)
     -  **Security Key (securityJsCode)** (alphanumeric string)

4. **Copy Both Keys**
   ```
   App Key: e.g., abc123def456...
   Security Key: e.g., xyz789abc123...
   ```

## Step 2: Configure in NeoSign

1. **Login to Admin Panel**

   - Log in with an administrator account.

2. **Go to Site Settings**

   - Click Top Navigation -> Settings.

3. **Fill Map Configuration**

   - **Map Provider**: Select `AMap (Gaode)`.
   - **Map API Key**: Paste your **App Key**.
   - **Map Security Key**: Paste your **Security Key (securityJsCode)**.
   - Click "Save".

## Step 3: Create Location Check-in Activity

1. **New Activity**

   - Go to "Activity Management" -> Click "Create Activity".

2. **Set Check-in Type**

   - Select: **Location** or **Location + QR Code**.

3. **Set Check-in Range**

   - Range: Enter radius (e.g., `50` meters).
   - Click "Use Current Location" to auto-fill your coordinates.

4. **View Visual Map**

   - If configured correctly, an AMap instance will appear below.
   - You will see:
     -  Center Marker (Check-in reference point)
     -  Blue Circle (Check-in range)
   - Click on the map to adjust the center.

5. **Save Activity**

   - Add participants.
   - Click "Save".

## Step 4: Test Check-in

1. **User Check-in**

   - Log in as a user and go to the check-in page.
   - Click "Check-in Now".
   - The system will auto-detect location and verify range.

2. **View Results**

   - Admins can view check-in records in activity stats.

## FAQ

### Q: Map does not show up?
**A:** Check:

1. Are both keys filled in?
2. Do the App Key and Security Key belong to the same application?
3. Check Browser Console (F12) for errors.
4. Common errors:
   - `INVALID_USER_KEY`: Key is incorrect.
   - `INVALID_USER_SCODE`: Security key is incorrect or missing.

### Q: How to verify configuration?
**A:**

1. Create a test activity with location check-in.
2. Click "Use Current Location". The map should appear.
3. If you see the map and blue circle, it works.

### Q: Where to find the Security Key?
**A:**

1. Login to AMap Console.
2. Application Management -> My Applications.
3. Find your app, click View.
4. In the Key list, each Key has a "Security Key" button.
5. Click to view and copy.

### Q: Do I need to bind a domain name?
**A:**

- Development phase: No.
- Production environment: It is recommended to set a "Domain Whitelist" in the console to improve security.

## Advanced Configuration (Optional)

### 1. Set Domain Whitelist
1. Console -> Key Management -> Settings.
2. Fill in your domain name (e.g., `neosign.example.com`).
3. Only requests initiated from this domain will be valid.

### 2. View Usage
- Console -> Data Statistics.
- You can view daily call counts.
- The free quota is usually sufficient (tens of thousands of calls per day).

### 3. Nginx Proxy Mode (More Secure)
If your application scale is large, you can refer to the AMap official documentation to configure Nginx proxy forwarding to avoid exposing the security key on the frontend:

- [Security Key Usage Instructions](https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode)

## Related Links

- [AMap Open Platform](https://lbs.amap.com/)
- [Console](https://console.amap.com/)
- [JavaScript API Docs](https://lbs.amap.com/api/jsapi-v2/summary)
- [Full Map SDK Integration Guide](MAP_SDK_GUIDE.md)

---

After configuration is complete, you can use the visual map to select points and create location check-in activities! If you have any questions, please refer to [Troubleshooting](MAP_SDK_GUIDE.md#troubleshooting) or submit an Issue.
