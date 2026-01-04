# 🚀 Vercel Deployment Checklist for Sloka 4.0

## ✅ Pre-Deployment Setup

### 1. Database Setup
- [ ] Create production Neon PostgreSQL database
- [ ] Note the connection string
- [ ] Test database connectivity

### 2. Blob Storage Setup  
- [ ] Create Vercel Blob storage
- [ ] Get read-write token
- [ ] Test file upload functionality

### 3. Environment Configuration
- [ ] Copy `.env.example` to create your production `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Update `PROD_DATABASE_URL` with your Neon database URL
- [ ] Update `PROD_BLOB_READ_WRITE_TOKEN` with your Vercel blob token
- [ ] Generate secure `SECRET_KEY` for JWT tokens
- [ ] Set strong `ADMIN_PASSWORD`

### 4. Vercel Account Setup
- [ ] Create Vercel account
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Login: `vercel login`

## 🚀 Deployment Process

### Option 1: Automated Deployment
```bash
./deploy_vercel.sh
```

### Option 2: Manual Deployment
```bash
vercel --prod
```

### Option 3: GitHub Integration
1. Push code to GitHub
2. Connect GitHub repo to Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy automatically on push

## 🔧 Environment Variables for Vercel Dashboard

Set these in your Vercel project settings:

```
ENVIRONMENT=production
PROD_DATABASE_URL=postgresql://username:password@host/database?sslmode=require
PROD_BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxxxxxxxxxx
SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@spiritual.com
ADMIN_PASSWORD=your-secure-admin-password
```

## 🧪 Post-Deployment Testing

### Test API Endpoints
```bash
# Test deployed application
python test_api.py https://your-app.vercel.app

# Manual tests
curl https://your-app.vercel.app/api/courses
curl https://your-app.vercel.app/
```

### Test Admin Login
1. Visit your deployed URL
2. Try admin login with your credentials
3. Test course creation/management
4. Test file uploads

### Test Student Flow
1. Register a test student account
2. Login as student
3. Browse available courses
4. Test course enrollment

## 🎯 Success Criteria

- [ ] Application loads without errors
- [ ] Admin login works
- [ ] Student registration works
- [ ] Courses display correctly
- [ ] File uploads work
- [ ] Database operations work
- [ ] No console errors

## 📊 Monitoring

- Monitor function logs in Vercel dashboard
- Check function execution times
- Monitor database connections
- Watch for any error patterns

## 🔄 Updates & Maintenance

For future updates:
```bash
# Deploy new version
git push origin main  # (if using GitHub integration)
# or
./deploy_vercel.sh
```

---
**Ready for spiritual course management in the cloud! 🕉️**
