# GitHub Actions Setup for GEE Automation

## 📋 Quick Setup Checklist

- [ ] Create GitHub repository (if not already done)
- [ ] Add GitHub Secrets
- [ ] Push code to GitHub
- [ ] Enable GitHub Actions
- [ ] Test workflow
- [ ] Monitor automated runs

---

## 🚀 Step-by-Step Setup

### Step 1: Create/Use GitHub Repository

If you don't have a GitHub repo yet:

```powershell
# Navigate to your project
cd "c:\Users\oseim\OneDrive\School\Final Year Project\Project"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Add GEE automation with GitHub Actions"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

---

### Step 2: Set Up Google Earth Engine Service Account

#### Option A: Use Personal Authentication (Easier)

1. **Authenticate Locally First:**
   ```powershell
   earthengine authenticate
   ```

2. **Get Your Credentials:**
   - After authentication, credentials are stored in:
     - Windows: `C:\Users\YOUR_USERNAME\.config\earthengine\credentials`
   - Open this file and copy the token

3. **Add to GitHub Secrets:**
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
   - Click "New repository secret"
   - Name: `EARTHENGINE_TOKEN`
   - Value: Paste the entire JSON from credentials file

#### Option B: Use Service Account (Recommended for Production)

1. **Create Service Account:**
   - Go to: https://console.cloud.google.com/
   - Enable Earth Engine API
   - Create Service Account
   - Download JSON key file

2. **Add to GitHub Secrets:**
   - Name: `GEE_SERVICE_ACCOUNT_KEY`
   - Value: Paste entire JSON key content

---

### Step 3: Add Supabase Secrets to GitHub

1. **Go to Repository Settings:**
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
   ```

2. **Add These Secrets:**

   | Secret Name | Value |
   |------------|-------|
   | `SUPABASE_URL` | `https://ntkzaobvbsppxbljamvb.supabase.co` |
   | `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your anon key) |

3. **Your Secrets Should Look Like This:**
   - ✓ SUPABASE_URL
   - ✓ SUPABASE_KEY
   - ✓ EARTHENGINE_TOKEN (or GEE_SERVICE_ACCOUNT_KEY)

---

### Step 4: Enable GitHub Actions

1. **Go to Your Repository**
2. **Click "Actions" Tab**
3. **If Disabled:** Click "I understand my workflows, go ahead and enable them"
4. **You Should See:** "Automated Satellite Data Collection" workflow

---

### Step 5: Test the Workflow (Manual Run)

1. **Go to Actions Tab**
2. **Click "Automated Satellite Data Collection"**
3. **Click "Run workflow" dropdown (right side)**
4. **Click green "Run workflow" button**
5. **Wait for it to complete (~2-5 minutes)**

---

### Step 6: Monitor Workflow Runs

**View Status:**
- Green checkmark ✓ = Success
- Red X = Failed (click to see logs)
- Yellow dot = Running

**Check Logs:**
1. Click on the workflow run
2. Click on "fetch-satellite-data" job
3. Expand steps to see detailed logs

**Expected Output:**
```
✅ Earth Engine initialized
✅ Supabase initialized
📡 Fetching Sentinel-2 data (last 30 days)
   Found 12 images
✅ RGB URL generated
✅ NDVI URL generated
✅ Database updated (ID: 10)
```

---

### Step 7: Verify in Supabase

1. **Go to Supabase Dashboard:**
   ```
   https://ntkzaobvbsppxbljamvb.supabase.co
   ```

2. **Check Database:**
   - Table Editor → `satellite_updates`
   - You should see a new record
   - Check `download_url` and `ndvi_url` fields

3. **Test Download URL:**
   - Copy the `download_url`
   - Paste in browser
   - Should download a GeoTIFF file

---

## ⏰ Automated Schedule

The workflow is configured to run:
- **Every 5 days at 2:00 AM UTC**
- **Manual trigger anytime** (via "Run workflow" button)

### Schedule Format (in workflow file):
```yaml
schedule:
  - cron: '0 2 */5 * *'
  #        │ │  │  │ │
  #        │ │  │  │ └─── day of week (0-6)
  #        │ │  │  └───── month (1-12)
  #        │ │  └──────── day of month (1-31)
  #        │ └─────────── hour (0-23, UTC)
  #        └───────────── minute (0-59)
```

### Want Different Schedule?

**Every 7 days:**
```yaml
schedule:
  - cron: '0 2 */7 * *'
```

**Every Monday at 3 AM:**
```yaml
schedule:
  - cron: '0 3 * * 1'
```

**Twice a month (1st and 15th):**
```yaml
schedule:
  - cron: '0 2 1,15 * *'
```

---

## 🐛 Troubleshooting

### Error: "Earth Engine not initialized"

**Solution:**
1. Check that `EARTHENGINE_TOKEN` secret is set correctly
2. Verify the token is valid (not expired)
3. Try re-authenticating locally and updating the secret

### Error: "Supabase connection failed"

**Solution:**
1. Check `SUPABASE_URL` and `SUPABASE_KEY` secrets
2. Make sure there are no extra spaces
3. Verify the API key hasn't been revoked

### Error: "No images found"

**Solution:**
1. This is normal - may not be images for every period
2. Workflow will succeed but skip upload
3. Will retry on next scheduled run

### Error: "Permission denied"

**Solution:**
1. Check GitHub Actions is enabled in repo settings
2. Verify secrets have correct permissions
3. Make sure workflow file is in `.github/workflows/` folder

### Workflow Not Running on Schedule

**Possible Causes:**
1. Repository must be active (have recent commits)
2. GitHub may delay by up to 15 minutes
3. Free tier may have usage limits
4. Check Actions tab for any disabled workflows

**Solution:**
- Make a commit to keep repo active
- Use manual trigger to test immediately
- Check GitHub Actions usage limits

---

## 📊 Monitor Usage

**GitHub Actions Free Tier:**
- ✓ 2,000 minutes/month for public repos
- ✓ Unlimited for public repos
- ⚠️ 2,000 minutes/month for private repos

**Your Workflow Uses:**
- ~3-5 minutes per run
- Every 5 days = ~6 runs/month
- Total: ~30 minutes/month (well within limits!)

---

## 🔔 Set Up Notifications

### Email Notifications:
1. Go to: https://github.com/settings/notifications
2. Enable "Actions" notifications
3. Choose "Only failures and first success"

### Slack Notifications (Optional):
Add to workflow file:
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] Workflow appears in Actions tab
- [ ] Manual run completes successfully
- [ ] New record appears in Supabase `satellite_updates` table
- [ ] Download URLs are accessible
- [ ] Scheduled runs appear in Actions tab (after 5 days)
- [ ] Email notifications working (if enabled)

---

## 📱 Next Steps

Now that GEE automation is running:

1. **Update Mobile App** to fetch from `satellite_updates` table
2. **Set up Colab trigger** (optional) to run U-Net on new imagery
3. **Monitor Supabase** for new satellite data every 5 days
4. **Enjoy automated mining detection!** 🎉

---

## 🆘 Need Help?

**GitHub Actions Docs:**
https://docs.github.com/en/actions

**Earth Engine Docs:**
https://developers.google.com/earth-engine

**Check Workflow Logs:**
- Actions tab → Click workflow run → View logs

**Test Locally First:**
```powershell
python gee_automation\gee_to_supabase.py
```

If local test works but GitHub Actions fails, it's likely a secrets configuration issue.

---

**Your automated satellite monitoring system is ready!** 🛰️✨
