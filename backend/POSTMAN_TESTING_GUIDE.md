# Postman Testing Guide - Fleet Management API

## Prerequisites

1. **Download Postman**: https://www.postman.com/downloads/
2. **Start the Django server**: `python manage.py runserver`
3. **Ensure Supabase is configured** in your `.env` file

---

## Step 1: Create a New Collection

1. Open Postman
2. Click **"New"** → **"Collection"**
3. Name it: `Fleet Management API`
4. Click **"Create"**

---

## Step 2: Set Up Environment Variables

1. Click **"Environments"** in the left sidebar
2. Click **"+"** to create a new environment
3. Name it: `Fleet Management Local`
4. Add these variables:

| Variable Name | Type | Initial Value | Current Value |
|--------------|------|---------------|---------------|
| `base_url` | default | `http://localhost:8000/api/v1` | `http://localhost:8000/api/v1` |
| `access_token` | default | (leave empty) | (leave empty) |
| `refresh_token` | default | (leave empty) | (leave empty) |
| `reset_access_token` | default | (leave empty) | (leave empty) |

5. Click **"Save"**
6. Select **"Fleet Management Local"** from the environment dropdown (top right corner)

---

## Step 3: Create API Requests

### Request 1: Register User

1. Click **"Add request"** in your collection
2. Name: `Register User`
3. Method: **POST**
4. URL: `{{base_url}}/auth/register/`
5. Go to **"Headers"** tab:
   - Key: `Content-Type`
   - Value: `application/json`
6. Go to **"Body"** tab:
   - Select **"raw"**
   - Select **"JSON"** from dropdown
   - Paste:
```json
{
  "email": "manager@fleet.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Manager",
  "phone_number": "+1234567890",
  "role": "fleet_manager"
}
```
7. Click **"Save"**

**Expected Response (201 Created):**
```json
{
  "message": "Sign up successful. Please check your email for verification OTP.",
  "user": {
    "id": "uuid-here",
    "email": "manager@fleet.com",
    "first_name": "John",
    "last_name": "Manager",
    "role": "fleet_manager",
    "email_verified": false
  },
  "email_verification_required": true
}
```

---

### Request 2: Verify OTP

1. Add new request
2. Name: `Verify OTP`
3. Method: **POST**
4. URL: `{{base_url}}/auth/verify-otp/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "email": "manager@fleet.com",
  "token": "123456"
}
```
*(Replace `123456` with the actual OTP from your email)*

7. Click **"Save"**

**Expected Response (200 OK):**
```json
{
  "message": "Email verified successfully",
  "verified": true
}
```

---

### Request 3: Resend OTP

1. Add new request
2. Name: `Resend OTP`
3. Method: **POST**
4. URL: `{{base_url}}/auth/resend-otp/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "email": "manager@fleet.com",
  "type": "signup"
}
```
7. Click **"Save"**

---

### Request 4: Login

1. Add new request
2. Name: `Login`
3. Method: **POST**
4. URL: `{{base_url}}/auth/login/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "email": "manager@fleet.com",
  "password": "SecurePass123!"
}
```
7. Go to **"Tests"** tab and add this script (auto-saves tokens):
```javascript
var jsonData = pm.response.json();

if (jsonData.access_token) {
    pm.environment.set("access_token", jsonData.access_token);
}

if (jsonData.refresh_token) {
    pm.environment.set("refresh_token", jsonData.refresh_token);
}

console.log("Tokens saved to environment!");
```
8. Click **"Save"**

**Expected Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid-here",
    "email": "manager@fleet.com",
    "first_name": "John",
    "last_name": "Manager",
    "role": "fleet_manager",
    "email_verified": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_at": "2026-01-22T22:00:00.000Z"
}
```

---

### Request 5: Get Profile

1. Add new request
2. Name: `Get Profile`
3. Method: **GET**
4. URL: `{{base_url}}/auth/profile/`
5. Go to **"Authorization"** tab:
   - Type: **Bearer Token**
   - Token: `{{access_token}}`
   
   *OR* go to **"Headers"** tab:
   - Key: `Authorization`
   - Value: `Bearer {{access_token}}`
6. Click **"Save"**

**Expected Response (200 OK):**
```json
{
  "id": "uuid-here",
  "email": "manager@fleet.com",
  "supabase_uid": "supabase-uid",
  "first_name": "John",
  "last_name": "Manager",
  "full_name": "John Manager",
  "phone_number": "+1234567890",
  "role": "fleet_manager",
  "is_active": true,
  "email_verified": true,
  "date_joined": "2026-01-22T19:00:00.000Z",
  "last_login": "2026-01-22T20:00:00.000Z",
  "updated_at": "2026-01-22T20:00:00.000Z"
}
```

---

### Request 6: Update Profile

1. Add new request
2. Name: `Update Profile`
3. Method: **PATCH**
4. URL: `{{base_url}}/auth/profile/`
5. Authorization: **Bearer Token** → `{{access_token}}`
6. Headers:
   - `Content-Type`: `application/json`
7. Body (raw JSON):
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+9876543210"
}
```
8. Click **"Save"**

---

### Request 7: Refresh Token

1. Add new request
2. Name: `Refresh Token`
3. Method: **POST**
4. URL: `{{base_url}}/auth/token/refresh/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "refresh_token": "{{refresh_token}}"
}
```
7. Go to **"Tests"** tab:
```javascript
var jsonData = pm.response.json();

if (jsonData.access_token) {
    pm.environment.set("access_token", jsonData.access_token);
    console.log("Access token updated!");
}

if (jsonData.refresh_token) {
    pm.environment.set("refresh_token", jsonData.refresh_token);
    console.log("Refresh token updated!");
}
```
8. Click **"Save"**

---

### Request 8: Password Reset Request

1. Add new request
2. Name: `Password Reset Request`
3. Method: **POST**
4. URL: `{{base_url}}/auth/password-reset/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "email": "manager@fleet.com"
}
```
7. Click **"Save"**

**Expected Response (200 OK):**
```json
{
  "message": "A 6-digit password reset code has been sent to your email.",
  "email": "manager@fleet.com"
}
```

---

### Request 9: Password Reset OTP Verify

1. Add new request
2. Name: `Password Reset OTP Verify`
3. Method: **POST**
4. URL: `{{base_url}}/auth/password-reset/verify-otp/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "email": "manager@fleet.com",
  "token": "123456"
}
```
*(Replace `123456` with the actual OTP from your email)*

7. Go to **"Tests"** tab and add this script (auto-saves token):
```javascript
var jsonData = pm.response.json();

if (jsonData.access_token) {
    pm.environment.set("reset_access_token", jsonData.access_token);
    console.log("Password reset token saved!");
}
```
8. Click **"Save"**

**Expected Response (200 OK):**
```json
{
  "message": "OTP verified successfully. You can now reset your password.",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "note": "Use this access_token to reset your password"
}
```

---

### Request 10: Password Reset Confirm

1. Add new request
2. Name: `Password Reset Confirm`
3. Method: **POST**
4. URL: `{{base_url}}/auth/password-reset/confirm/`
5. Headers:
   - `Content-Type`: `application/json`
6. Body (raw JSON):
```json
{
  "access_token": "{{reset_access_token}}",
  "new_password": "NewSecurePass123!"
}
```
7. Click **"Save"**

**Expected Response (200 OK):**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

---

### Request 11: Logout

1. Add new request
2. Name: `Logout`
3. Method: **POST**
4. URL: `{{base_url}}/auth/logout/`
5. Authorization: **Bearer Token** → `{{access_token}}`
6. Click **"Save"**

---

## Step 4: Organize Your Collection

Create folders in your collection:

### Folder 1: Authentication
- Register User
- Verify OTP
- Resend OTP
- Login
- Logout
- Password Reset Request
- Password Reset OTP Verify
- Password Reset Confirm

### Folder 2: Token Management
- Refresh Token

### Folder 3: User Profile
- Get Profile
- Update Profile

---

## Testing Workflow

### Complete Test Sequence

1. **Start Server**
   ```bash
   python manage.py runserver
   ```

2. **Register User**
   - Click **"Register User"** request
   - Click **"Send"**
   - Check response status: `201 Created`

3. **Check Email**
   - Go to your email inbox
   - Find OTP code (6 digits)

4. **Verify OTP**
   - Click **"Verify OTP"** request
   - Replace `123456` with your actual OTP
   - Click **"Send"**
   - Check response: `verified: true`

5. **Login**
   - Click **"Login"** request
   - Click **"Send"**
   - Tokens are automatically saved to environment
   - Check **Console** (bottom) for "Tokens saved" message

6. **Get Profile**
   - Click **"Get Profile"** request
   - Click **"Send"**
   - You should see your user details

7. **Update Profile**
   - Click **"Update Profile"** request
   - Modify the JSON body as needed
   - Click **"Send"**

8. **Test Token Refresh**
   - Wait for token to expire (or force test)
   - Click **"Refresh Token"** request
   - Click **"Send"**
   - New access token is saved automatically

9. **Logout**
   - Click **"Logout"** request
   - Click **"Send"**

---

## Testing Different User Roles

### Test Superuser
```json
{
  "email": "admin@fleet.com",
  "password": "AdminPass123!",
  "role": "superuser"
}
```

### Test Fleet Manager
```json
{
  "email": "manager@fleet.com",
  "password": "ManagerPass123!",
  "role": "fleet_manager"
}
```

### Test Transport Supervisor
```json
{
  "email": "supervisor@fleet.com",
  "password": "SupervisorPass123!",
  "role": "transport_supervisor"
}
```

---

## Troubleshooting

### Issue: "Cannot connect to server"
**Solution:**
- Ensure server is running: `python manage.py runserver`
- Check URL: `http://localhost:8000/api/v1`

### Issue: "Invalid or expired token"
**Solution:**
- Use the **Refresh Token** request
- Or login again to get new tokens

### Issue: "Environment variable not working"
**Solution:**
- Ensure environment is selected (top right dropdown)
- Check variables are spelled correctly with double curly braces: `{{base_url}}`

### Issue: "OTP verification failed"
**Solution:**
- Check your email (including spam folder)
- OTP expires after a few minutes
- Use **Resend OTP** request if expired

### Issue: "User already exists"
**Solution:**
- Use a different email
- Or login with existing credentials

---

## Pro Tips

✅ **Use Collection Runner** for automated testing of multiple requests

✅ **Save responses as examples** for documentation

✅ **Use Pre-request Scripts** for dynamic data:
```javascript
pm.environment.set("timestamp", Date.now());
```

✅ **Check Console** (bottom panel) for debugging info

✅ **Use Variables** for different environments (dev, staging, prod)

✅ **Export Collection** to share with team members

---

## Export/Import Collection

### To Export:
1. Right-click on collection
2. Click **"Export"**
3. Save JSON file

### To Import:
1. Click **"Import"** button (top left)
2. Select JSON file
3. Collection is imported with all requests

---

## Keyboard Shortcuts

- `Ctrl + Enter` - Send request
- `Ctrl + S` - Save request
- `Ctrl + /` - Search collections
- `Ctrl + K` - Command palette

---

## Next Steps

After authentication works:
1. Test with all three user roles
2. Test error scenarios (wrong password, invalid email, etc.)
3. Test token expiration and refresh
4. Create automated test scripts
5. Add vehicle management endpoints
6. Add driver management endpoints

---

## Resources

- **Postman Docs**: https://learning.postman.com/
- **Django API**: http://localhost:8000/admin/
- **Supabase Dashboard**: https://supabase.com/dashboard
- **API Documentation**: See `API_TESTING_GUIDE.md`

---

**Happy Testing! 🚀**
