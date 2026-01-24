# Fleet Management Backend - Render Deployment Guide

## Prerequisites

- GitHub account with your code pushed
- Render account (sign up at https://render.com)
- Supabase database already set up and running

## Step 1: Prepare Your Repository

1. **Ensure all deployment files are committed:**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Files needed for deployment:**
   - ✅ `requirements.txt` - Python dependencies (including gunicorn)
   - ✅ `build.sh` - Build script for Render
   - ✅ `render.yaml` - Render configuration (optional but recommended)
   - ✅ Updated `settings.py` with production settings

## Step 2: Update Requirements.txt

Make sure `gunicorn` and `whitenoise` are in your `requirements.txt`. They should already be included.

## Step 3: Update settings.py for Production

The settings.py has been updated with:
- ✅ Static files configuration
- ✅ Security middleware (whitenoise)
- ✅ Database connection pooling
- ✅ Environment-based DEBUG setting
- ✅ Dynamic ALLOWED_HOSTS

## Step 4: Create Web Service on Render

### Option A: Using the Render Dashboard (Recommended)

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Click "New +" button
   - Select "Web Service"

2. **Connect Your Repository:**
   - Choose "Build and deploy from a Git repository"
   - Click "Connect GitHub" (or GitLab/other)
   - Authorize Render to access your repositories
   - Select your `fleet-management` repository
   - Click "Connect"

3. **Configure Web Service:**
   
   **Basic Settings:**
   - **Name:** `fleet-management-backend` (or your preferred name)
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`

4. **Select Instance Type:**
   - **Free:** For testing (spins down after inactivity)
   - **Starter ($7/month):** For production (always on)
   - **Standard ($25/month):** For higher traffic

5. **Add Environment Variables:**
   
   Click "Advanced" then add these environment variables:
   
   ```
   PYTHON_VERSION=3.11.0
   DEBUG=False
   SECRET_KEY=<generate-a-strong-random-key>
   ALLOWED_HOSTS=.onrender.com
   
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-public-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   
   # Database Configuration
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres.your-project-ref
   SUPABASE_DB_PASSWORD=your-database-password
   SUPABASE_DB_HOST=db.your-project-ref.supabase.co
   SUPABASE_DB_PORT=5432
   
   # JWT Configuration
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   **How to get Supabase credentials:**
   - Go to your Supabase dashboard
   - **URL & Keys:** Project Settings → API → URL and anon/service_role keys
   - **Database:** Project Settings → Database → Connection string (Direct connection)
     - Host: `db.xxxxxxxxxxxxx.supabase.co`
     - Database: `postgres`
     - Port: `5432`
     - User: `postgres.xxxxxxxxxxxxx`
     - Password: Your database password

6. **Create Web Service:**
   - Click "Create Web Service"
   - Render will start building and deploying your app

### Option B: Using render.yaml (Blueprint)

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Click "New +" button
   - Select "Blueprint"

2. **Connect Repository:**
   - Choose your `fleet-management` repository
   - Render will detect the `render.yaml` file

3. **Configure Environment Variables:**
   - Fill in all the required environment variables
   - Click "Apply"

## Step 5: Monitor Deployment

1. **Watch Build Logs:**
   - Render will show real-time logs
   - Wait for "Build successful" message
   - Then wait for "Deploy succeeded"

2. **Check for Errors:**
   - If build fails, check the logs
   - Common issues:
     - Missing dependencies in requirements.txt
     - Build script permissions (fix: `chmod +x build.sh`)
     - Environment variables not set

3. **Get Your URL:**
   - Once deployed, Render provides a URL: `https://fleet-management-backend.onrender.com`
   - Copy this URL for your frontend configuration

## Step 6: Update Frontend Configuration

Update your Vercel frontend environment variables:

```
NEXT_PUBLIC_API_URL=https://your-backend-app.onrender.com
```

## Step 7: Update CORS Settings

After deployment, update your Django settings to allow your frontend:

1. **Get your Vercel frontend URL** (e.g., `https://fleet-management.vercel.app`)

2. **Update ALLOWED_HOSTS in Render dashboard:**
   ```
   ALLOWED_HOSTS=.onrender.com,fleet-management.vercel.app
   ```

3. **Add CORS_ALLOWED_ORIGINS as environment variable:**
   ```
   CORS_ALLOWED_ORIGINS=https://fleet-management.vercel.app,https://your-frontend-domain.vercel.app
   ```

   Or modify settings.py to read from environment:
   - Add to your Render environment variables
   - Update automatically on redeploy

## Step 8: Test Your Deployment

1. **Health Check:**
   - Visit: `https://your-app.onrender.com/admin/`
   - You should see Django admin login page

2. **API Test:**
   - Visit: `https://your-app.onrender.com/api/v1/`
   - Should see Django REST Framework browsable API

3. **Test Authentication:**
   - Try logging in from your frontend
   - Verify API calls work correctly

## Common Issues & Solutions

### Issue 1: Build Fails - Permission Denied on build.sh

**Solution:**
```bash
# On your local machine:
chmod +x backend/build.sh
git add backend/build.sh
git commit -m "Make build.sh executable"
git push
```

Then redeploy on Render.

### Issue 2: Static Files Not Loading

**Solution:**
- Ensure `whitenoise` is in requirements.txt
- Verify `STATIC_ROOT` is set in settings.py
- Check build logs for collectstatic errors

### Issue 3: Database Connection Fails

**Solution:**
- Verify all database environment variables are correct
- Check Supabase database is accessible (not paused)
- Ensure IP is whitelisted in Supabase (Render IPs can change)
- Consider using connection pooling (already configured)

### Issue 4: CORS Errors

**Solution:**
- Add your Vercel frontend URL to `CORS_ALLOWED_ORIGINS`
- Ensure `corsheaders` middleware is in MIDDLEWARE
- Check environment variables are set correctly

### Issue 5: Free Tier Spins Down

**Behavior:**
- Free tier services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Not suitable for production

**Solutions:**
- Upgrade to Starter plan ($7/month) for always-on service
- Use a uptime monitoring service (free tier for testing)

### Issue 6: Environment Variables Not Working

**Solution:**
- Ensure all required environment variables are set in Render dashboard
- Use quotes for values with special characters
- Restart service after updating environment variables

### Issue 7: Migrations Not Running

**Solution:**
- Check build logs to see if migrations ran
- Manually run migrations from Render shell:
  - Go to your service → Shell
  - Run: `python manage.py migrate`

## Updating Your Deployment

When you push changes to GitHub:

1. **Automatic Deployment:**
   - Render automatically detects changes
   - Rebuilds and redeploys
   - Takes 2-5 minutes

2. **Manual Deployment:**
   - Go to your service in Render dashboard
   - Click "Manual Deploy" → "Deploy latest commit"

3. **Rollback:**
   - Go to "Events" tab
   - Click "Rollback" on a previous successful deploy

## Managing Your Service

### View Logs

- **Build Logs:** See what happened during build
- **Deploy Logs:** See deployment process
- **Application Logs:** See your Django logs (print statements, errors)

### Shell Access

- Go to your service → "Shell" tab
- Access Django shell: `python manage.py shell`
- Run management commands
- Inspect database

### Metrics (Paid Plans)

- CPU usage
- Memory usage
- Request counts
- Response times

## Security Best Practices

1. **Never commit sensitive data:**
   - Use environment variables for all secrets
   - Add `.env` to `.gitignore`

2. **Use strong SECRET_KEY:**
   - Generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
   - Set in Render environment variables

3. **Set DEBUG=False in production:**
   - Already configured to read from environment
   - Ensure DEBUG=False in Render

4. **Restrict ALLOWED_HOSTS:**
   - Only allow your Render domain
   - Add frontend domain if needed

5. **Keep dependencies updated:**
   - Regularly update requirements.txt
   - Test updates before deploying

## Cost Estimation

**Free Tier:**
- ✅ Free forever
- ⚠️ Spins down after 15 min inactivity
- ⚠️ 750 hours/month (then spins down)
- 🎯 Good for: Development, testing, personal projects

**Starter ($7/month):**
- ✅ Always on (no spin down)
- ✅ 512 MB RAM
- ✅ 0.5 CPU
- 🎯 Good for: Small production apps, startups

**Standard ($25/month):**
- ✅ 2 GB RAM
- ✅ 1 CPU
- ✅ Better performance
- 🎯 Good for: Growing apps, more traffic

## Post-Deployment Checklist

- [ ] Backend deployed successfully on Render
- [ ] All environment variables configured
- [ ] Database migrations ran successfully
- [ ] Static files collected and serving
- [ ] Admin panel accessible
- [ ] API endpoints responding
- [ ] Frontend can connect to backend
- [ ] CORS configured correctly
- [ ] Authentication working
- [ ] Test all major features
- [ ] Check logs for errors
- [ ] Set up monitoring (optional)

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **Render Community:** https://community.render.com/

## Next Steps

After successful deployment:

1. **Set up monitoring** (optional)
   - Use Render metrics
   - Set up Sentry for error tracking
   - Configure logging

2. **Set up backups**
   - Supabase handles database backups
   - Consider downloading periodic backups

3. **Performance optimization**
   - Enable Redis caching (if needed)
   - Optimize database queries
   - Monitor response times

4. **CI/CD** (optional)
   - Set up GitHub Actions
   - Automated testing before deployment
   - Automated deployment on merge

---

**Deployment Complete!** 🚀

Your Django backend should now be live on Render. If you encounter any issues, check the logs in the Render dashboard and refer to the troubleshooting section above.
