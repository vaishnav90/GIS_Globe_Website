#!/usr/bin/env python3
"""
Google Cloud Setup Script for National 4-H GIS Leadership Team Website
This script helps you set up authentication and create necessary resources.
"""

import os
import json
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return None

def check_gcloud_installed():
    """Check if gcloud CLI is installed."""
    try:
        subprocess.run(["gcloud", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_google_cloud():
    """Main setup function."""
    print("🚀 Google Cloud Setup for National 4-H GIS Leadership Team Website")
    print("=" * 70)
    
    # Check if gcloud is installed
    if not check_gcloud_installed():
        print("❌ Google Cloud SDK is not installed!")
        print("📥 Please install it from: https://cloud.google.com/sdk/docs/install")
        print("   Then run this script again.")
        return False
    
    # Get project details
    print("\n📋 Project Configuration:")
    project_id = input("Enter your Google Cloud Project ID (or press Enter to create new): ").strip()
    
    if not project_id:
        project_name = input("Enter project name (e.g., 'national-4h-gis-team'): ").strip()
        if not project_name:
            print("❌ Project name is required!")
            return False
        
        # Create new project
        result = run_command(f"gcloud projects create {project_name} --name='National 4-H GIS Team'", 
                           f"Creating project '{project_name}'")
        if not result:
            return False
        project_id = project_name
    
    # Set project
    result = run_command(f"gcloud config set project {project_id}", 
                        f"Setting project to '{project_id}'")
    if not result:
        return False
    
    # Enable required APIs
    apis = [
        "storage.googleapis.com",
        "appengine.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com"
    ]
    
    for api in apis:
        result = run_command(f"gcloud services enable {api}", 
                           f"Enabling {api}")
        if not result:
            return False
    
    # Create storage bucket
    bucket_name = f"{project_id}-data"
    result = run_command(f"gsutil mb gs://{bucket_name}", 
                        f"Creating storage bucket '{bucket_name}'")
    if not result:
        return False
    
    # Make bucket publicly readable for images
    result = run_command(f"gsutil iam ch allUsers:objectViewer gs://{bucket_name}", 
                        f"Setting bucket permissions")
    if not result:
        return False
    
    # Create service account
    service_account_name = "national-4h-gis-app"
    service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    result = run_command(f"gcloud iam service-accounts create {service_account_name} --display-name='National 4-H GIS App'", 
                        f"Creating service account '{service_account_name}'")
    if not result:
        # Service account might already exist
        print("⚠️  Service account might already exist, continuing...")
    
    # Grant necessary permissions
    permissions = [
        "storage.objects.create",
        "storage.objects.delete",
        "storage.objects.get",
        "storage.objects.list",
        "storage.objects.update"
    ]
    
    for permission in permissions:
        result = run_command(f"gcloud projects add-iam-policy-binding {project_id} --member=serviceAccount:{service_account_email} --role=roles/storage.{permission.split('.')[-1]}", 
                           f"Granting {permission} permission")
        if not result:
            return False
    
    # Create and download service account key
    key_file = "service-account-key.json"
    result = run_command(f"gcloud iam service-accounts keys create {key_file} --iam-account={service_account_email}", 
                        f"Creating service account key file")
    if not result:
        return False
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_hex(32)
    
    # Create environment file
    env_content = f"""# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT={project_id}
STORAGE_BUCKET={bucket_name}
SECRET_KEY={secret_key}

# Service Account (for local development)
GOOGLE_APPLICATION_CREDENTIALS={os.path.abspath(key_file)}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Update app.yaml
    app_yaml_content = f"""runtime: python311
entrypoint: gunicorn -b :$PORT main_cloud:app

env_variables:
  GOOGLE_CLOUD_PROJECT: "{project_id}"
  STORAGE_BUCKET: "{bucket_name}"
  SECRET_KEY: "{secret_key}"

instance_class: F1

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10

handlers:
- url: /static
  static_dir: static
- url: /.*
  script: auto
"""
    
    with open('app.yaml', 'w') as f:
        f.write(app_yaml_content)
    
    # Create deployment instructions
    deployment_instructions = f"""# Deployment Instructions

## 🚀 Quick Deploy

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test locally:**
   ```bash
   python main_cloud.py
   ```

3. **Deploy to Google Cloud:**
   ```bash
   gcloud app deploy
   ```

## 🔐 Authentication

The service account key file `{key_file}` has been created for local development.
For production deployment, App Engine will use the default service account automatically.

## 📊 Storage Bucket

Your data will be stored in: `gs://{bucket_name}`

## 🌐 Access Your App

After deployment, your app will be available at:
https://{project_id}.appspot.com

## 🔒 Security Notes

- Keep the `{key_file}` file secure and never commit it to version control
- The secret key in app.yaml should be changed in production
- Consider using Google Secret Manager for sensitive data in production
"""
    
    with open('DEPLOYMENT_INSTRUCTIONS.md', 'w') as f:
        f.write(deployment_instructions)
    
    print("\n🎉 Setup completed successfully!")
    print(f"\n📁 Files created:")
    print(f"   - {key_file} (service account key)")
    print(f"   - .env (environment variables)")
    print(f"   - app.yaml (updated deployment config)")
    print(f"   - DEPLOYMENT_INSTRUCTIONS.md (deployment guide)")
    
    print(f"\n🔐 Authentication configured:")
    print(f"   - Project ID: {project_id}")
    print(f"   - Storage Bucket: {bucket_name}")
    print(f"   - Service Account: {service_account_email}")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Install dependencies: pip install -r requirements.txt")
    print(f"   2. Test locally: python main_cloud.py")
    print(f"   3. Deploy: gcloud app deploy")
    
    return True

if __name__ == "__main__":
    setup_google_cloud() 