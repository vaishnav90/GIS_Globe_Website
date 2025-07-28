# Deployment Guide for Google Cloud

This guide will help you deploy your Flask application with authentication to Google Cloud Platform.

## Prerequisites

1. Google Cloud SDK installed
2. A Google Cloud Project
3. Billing enabled on your project

## Database Setup

### Option 1: Cloud SQL (PostgreSQL) - Recommended for Production

1. **Create a Cloud SQL instance:**
   ```bash
   gcloud sql instances create your-instance-name \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1 \
     --root-password=your-root-password
   ```

2. **Create a database:**
   ```bash
   gcloud sql databases create your-database-name \
     --instance=your-instance-name
   ```

3. **Create a user:**
   ```bash
   gcloud sql users create your-username \
     --instance=your-instance-name \
     --password=your-password
   ```

4. **Get the connection string:**
   ```bash
   gcloud sql instances describe your-instance-name \
     --format="value(connectionName)"
   ```

5. **Set the DATABASE_URL environment variable:**
   ```bash
   gcloud app deploy --set-env-vars DATABASE_URL="postgresql://your-username:your-password@/your-database-name?host=/cloudsql/your-project:us-central1:your-instance-name"
   ```

### Option 2: Cloud Firestore (NoSQL)

For a simpler setup, you can use Cloud Firestore instead of PostgreSQL.

## Environment Variables

Set these environment variables in your Google App Engine:

```bash
gcloud app deploy --set-env-vars \
  SECRET_KEY="your-secure-secret-key" \
  FLASK_ENV="production"
```

## Deployment Steps

1. **Initialize your project:**
   ```bash
   gcloud init
   gcloud config set project your-project-id
   ```

2. **Enable required APIs:**
   ```bash
   gcloud services enable appengine.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

3. **Deploy to App Engine:**
   ```bash
   gcloud app deploy
   ```

4. **View your application:**
   ```bash
   gcloud app browse
   ```

## Security Considerations

1. **Change the SECRET_KEY** in app.yaml to a secure random string
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** (already configured in app.yaml)
4. **Set up proper IAM roles** for your service account

## Database Migration

After deployment, you'll need to create the database tables. You can do this by:

1. **Accessing the App Engine console**
2. **Going to your deployed application**
3. **The tables will be created automatically on first run**

## Monitoring

1. **View logs:**
   ```bash
   gcloud app logs tail -s default
   ```

2. **Monitor performance** in the Google Cloud Console

## Troubleshooting

### Common Issues:

1. **Database connection errors:**
   - Check your DATABASE_URL format
   - Ensure Cloud SQL instance is running
   - Verify network connectivity

2. **Import errors:**
   - Make sure all dependencies are in requirements.txt
   - Check Python version compatibility

3. **Authentication issues:**
   - Verify SECRET_KEY is set
   - Check session configuration

## Local Development

For local development with the same database:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your-dev-secret-key
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Production Checklist

- [ ] SECRET_KEY changed to secure value
- [ ] Database properly configured
- [ ] HTTPS enabled
- [ ] Environment variables set
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Error logging enabled 