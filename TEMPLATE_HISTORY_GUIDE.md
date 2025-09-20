# 📋 Template and History Management Guide

## 🔐 **Authentication Required**

Before using templates and history, you need to register and login:

### **Step 1: Register a User**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"username": "yourusername", "email": "your@email.com", "password": "yourpassword", "full_name": "Your Name"}'
```

### **Step 2: Login to Get Token**
```powershell
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/x-www-form-urlencoded" -Body "username=yourusername&password=yourpassword"
$token = $loginResponse.access_token
```

---

## 📁 **Template Management**

### **Save a Signature as Template**

When uploading a signature, you can save it as a template:

```powershell
# Upload signature and save as template
$headers = @{ "Authorization" = "Bearer $token" }
$form = @{
    file = Get-Item "path/to/your/signature.jpg"
    template_name = "My Signature Template"
}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/signature/upload" -Method POST -Headers $headers -Form $form
```

### **View Your Templates**

```powershell
$headers = @{ "Authorization" = "Bearer $token" }
$templates = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/signature/templates" -Method GET -Headers $headers
$templates.templates
```

### **Delete a Template**

```powershell
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/signature/templates/1" -Method DELETE -Headers $headers
```

---

## 📊 **History Management**

### **View Verification History**

```powershell
$headers = @{ "Authorization" = "Bearer $token" }
$history = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/signature/history?limit=20" -Method GET -Headers $headers
$history.verification_history
```

### **Get User Statistics**

```powershell
$headers = @{ "Authorization" = "Bearer $token" }
$stats = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/signature/stats" -Method GET -Headers $headers
$stats
```

---

## 🎯 **Using Templates for Verification**

### **Verify Against a Template**

```powershell
$headers = @{ "Authorization" = "Bearer $token" }
$form = @{
    file = Get-Item "path/to/signature/to/verify.jpg"
    template_id = "1"  # ID of your saved template
}
$result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/signature/verify" -Method POST -Headers $headers -Form $form
$result.analysis_result
```

---

## 🌐 **Frontend Usage**

### **1. Open the Frontend**
- Open `frontend/index.html` in your browser
- The interface has 4 main tabs:
  - **Upload & Analyze**: Upload signatures and optionally save as templates
  - **Verify Against Template**: Compare signatures with saved templates
  - **My Templates**: View and manage your saved templates
  - **History**: View your verification history

### **2. Save Templates**
1. Go to **Upload & Analyze** tab
2. Upload or draw a signature
3. Enter a template name in the "Save as Template" field
4. Click "Analyze Signature"
5. The signature will be saved as a template

### **3. Use Templates**
1. Go to **Verify Against Template** tab
2. Upload a signature to verify
3. Select a template from the dropdown
4. Click "Verify Signature"
5. Get comparison results

### **4. Manage Templates**
1. Go to **My Templates** tab
2. View all your saved templates
3. Delete templates you no longer need
4. Refresh to see updates

### **5. View History**
1. Go to **History** tab
2. See all your verification attempts
3. View authenticity scores and confidence levels
4. Track processing times

---

## 🔧 **API Endpoints Summary**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login and get token |
| `/api/v1/signature/upload` | POST | Upload signature (optionally save as template) |
| `/api/v1/signature/verify` | POST | Verify signature against template |
| `/api/v1/signature/templates` | GET | List user templates |
| `/api/v1/signature/templates/{id}` | DELETE | Delete template |
| `/api/v1/signature/history` | GET | Get verification history |
| `/api/v1/signature/stats` | GET | Get user statistics |

---

## 📝 **Example Workflow**

1. **Register and Login**
2. **Upload First Signature** → Save as "My Original Signature"
3. **Upload Second Signature** → Save as "My Backup Signature"
4. **Verify New Signature** → Compare against "My Original Signature"
5. **View Results** → Check authenticity score and confidence
6. **Review History** → See all verification attempts
7. **Manage Templates** → Delete old templates, keep current ones

---

## ⚠️ **Important Notes**

- **Authentication Required**: All template and history operations require login
- **Token Expiry**: Tokens expire after 30 minutes, re-login if needed
- **File Formats**: Supports JPG, PNG, BMP, TIFF
- **File Size**: Maximum 10MB per file
- **Privacy**: All data stored locally in SQLite database

---

## 🎉 **Ready to Use!**

Your signature recognition system is fully functional with:
- ✅ Template management
- ✅ History tracking
- ✅ User authentication
- ✅ Signature verification
- ✅ Real-time analysis

Start by opening `frontend/index.html` in your browser and follow the workflow above!
