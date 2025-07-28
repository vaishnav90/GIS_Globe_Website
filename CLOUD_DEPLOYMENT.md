# Cloud Storage Deployment Guide

This guide will help you deploy the National 4-H GIS Leadership Team website using Google Cloud Storage for all data persistence.

## 🚀 **What's Changed**

### **Database Migration**
- **From**: SQLite database (local file)
- **To**: Google Cloud Storage buckets (cloud-native)
- **Benefits**: 
  - Persistent across deployments
  - Scalable and reliable
  - No database setup required
  - Automatic backups

### **File Storage**
- **From**: Local file system
- **To**: Google Cloud Storage
- **Benefits**:
  - Images persist across deployments
  - Global CDN access
  - Automatic scaling

## 📋 **Prerequisites**

1. **Google Cloud Account**
   - Create a Google Cloud project
   - Enable billing
   - Install Google Cloud SDK

2. **Required APIs**
   - Cloud Storage API
   - App Engine API

## 🔧 **Setup Steps**

### **1. Install Google Cloud SDK**
```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
gcloud init
gcloud auth application-default login
```

### **2. Create Google Cloud Project**
```bash
gcloud projects create national-4h-gis-team --name="National 4-H GIS Team"
gcloud config set project national-4h-gis-team
```

### **3. Enable Required APIs**
```bash
gcloud services enable storage.googleapis.com
gcloud services enable appengine.googleapis.com
```

### **4. Create Storage Bucket**
```bash
gsutil mb gs://national-4h-gis-team-data
gsutil iam ch allUsers:objectViewer gs://national-4h-gis-team-data
```

### **5. Update Configuration**

#### **Update app.yaml**
```yaml
env_variables:
  GOOGLE_CLOUD_PROJECT: "national-4h-gis-team"
  STORAGE_BUCKET: "national-4h-gis-team-data"
  SECRET_KEY: "your-secure-secret-key-here"
```

#### **Generate Secret Key**
```python
import secrets
print(secrets.token_hex(32))
```

### **6. Install Dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 **Deployment**

### **1. Deploy to App Engine**
```bash
gcloud app deploy
```

### **2. Set Up Custom Domain (Optional)**
```bash
gcloud app domain-mappings create your-domain.com
```

### **3. Monitor Deployment**
```bash
gcloud app logs tail -s default
```

## 📊 **Data Structure**

### **Cloud Storage Bucket Organization**
```
national-4h-gis-team-data/
├── users/
│   ├── user-id-1.json
│   ├── user-id-2.json
│   └── ...
├── projects/
│   ├── project-id-1.json
│   ├── project-id-2.json
│   └── ...
├── gallery/
│   ├── item-id-1.json
│   ├── item-id-2.json
│   └── ...
├── contact_messages/
│   ├── message-id-1.json
│   ├── message-id-2.json
│   └── ...
└── uploads/
    ├── 20241227_143022_image1.jpg
    ├── 20241227_143023_image2.png
    └── ...
```

### **JSON Data Format**

#### **User Data**
```json
{
  "id": "uuid-string",
  "username": "username",
  "email": "user@example.com",
  "password_hash": "hashed-password",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2024-12-27T14:30:22.123456",
  "last_login": "2024-12-27T15:45:33.654321",
  "is_active": true
}
```

#### **Project Data**
```json
{
  "id": "uuid-string",
  "title": "Project Title",
  "description": "Project description",
  "project_link": "https://example.com/project",
  "project_type": "Web App",
  "tags": "GIS, Mapping, Analysis",
  "image_url": "https://storage.googleapis.com/bucket/uploads/image.jpg",
  "created_at": "2024-12-27T14:30:22.123456",
  "updated_at": "2024-12-27T14:30:22.123456",
  "created_by": "user-id",
  "is_active": true
}
```

## 🔐 **Security Features**

### **Authentication**
- Email domain restriction (`@national4hgeospatialteam.us`)
- Password hashing with Werkzeug
- Session management with Flask-Login

### **Authorization**
- Creator-only edit/delete permissions
- Role-based access control
- Secure file uploads

### **Data Protection**
- Soft deletion (data marked inactive, not deleted)
- Input validation and sanitization
- Secure file handling

## 📈 **Scaling Benefits**

### **Automatic Scaling**
- App Engine handles traffic spikes
- Automatic instance management
- Global load balancing

### **Storage Scaling**
- Unlimited storage capacity
- Automatic backup and redundancy
- Global CDN for fast access

### **Cost Optimization**
- Pay only for what you use
- Automatic scaling down during low traffic
- No server maintenance costs

## 🛠 **Maintenance**

### **Backup Data**
```bash
# Export all data
gsutil -m cp -r gs://national-4h-gis-team-data ./backup/
```

### **Monitor Usage**
```bash
# View storage usage
gsutil du -sh gs://national-4h-gis-team-data/

# View app logs
gcloud app logs tail
```

### **Update Application**
```bash
# Deploy updates
gcloud app deploy

# Rollback if needed
gcloud app versions list
gcloud app services set-traffic default --splits=version-id=1.0
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Authentication Errors**
```bash
# Re-authenticate
gcloud auth application-default login
```

#### **2. Storage Permission Errors**
```bash
# Check bucket permissions
gsutil iam get gs://national-4h-gis-team-data
```

#### **3. App Engine Errors**
```bash
# View detailed logs
gcloud app logs tail --level=debug
```

### **Performance Optimization**

#### **1. Enable Caching**
```yaml
# In app.yaml
handlers:
- url: /static
  static_dir: static
  http_headers:
    Cache-Control: public, max-age=31536000
```

#### **2. Optimize Images**
- Use WebP format when possible
- Compress images before upload
- Implement lazy loading

## 📞 **Support**

For deployment issues:
1. Check Google Cloud Console logs
2. Review App Engine documentation
3. Contact Google Cloud support

For application issues:
1. Check application logs
2. Review error messages
3. Test locally first

## 🎉 **Success Metrics**

After deployment, verify:
- ✅ User registration works
- ✅ Login/logout functions
- ✅ Project creation and editing
- ✅ Gallery image uploads
- ✅ Contact form submissions
- ✅ Email domain restrictions
- ✅ File uploads to cloud storage
- ✅ Data persistence across deployments

Your website is now fully cloud-native and ready for production use! 🚀 