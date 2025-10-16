# Deploy to Streamlit Cloud - Step-by-Step Guide

**Get your interactive UI online in 10 minutes!**

---

## Prerequisites

- ✅ GitHub account (you have this)
- ✅ Code ready in GitHub repo (synced)
- ✅ FalkorDB Cloud instance running (done!)

---

## Step 1: Push to GitHub (5 minutes)

### 1a. Check Current Status

```bash
cd /Users/liz/Documents/GitHub/Negotiation-Continuity-Experiment
git status
```

You should see:
- Modified: `app.py`, `.env` (don't commit this!), other files
- New files: `SHARE_WITH_BOSS.md`, `requirements.txt`, etc.

### 1b. Stage Files for Commit

```bash
# Add all files EXCEPT .env (contains passwords)
git add .
git reset .env  # Remove .env from staging

# Or be selective:
git add app.py
git add requirements.txt
git add SHARE_WITH_BOSS.md
git add export/
git add .streamlit/
git add scripts/
```

### 1c. Create Commit

```bash
git commit -m "Add cloud-enabled Streamlit UI and FalkorDB Cloud integration

- Updated app.py to support both local and cloud FalkorDB
- Added requirements.txt for Streamlit Cloud deployment
- Created comprehensive SHARE_WITH_BOSS.md guide
- Exported RDB backup for cloud import
- All 206 nodes and 73 relationships now in cloud

Ready for Streamlit Cloud deployment!"
```

### 1d. Push to GitHub

```bash
git push origin main
```

If you don't have a remote set up:
```bash
# First time only
git remote add origin https://github.com/YOUR_USERNAME/Negotiation-Continuity-Experiment.git
git push -u origin main
```

---

## Step 2: Deploy to Streamlit Cloud (5 minutes)

### 2a. Go to Streamlit Cloud

1. Visit: https://share.streamlit.io/
2. Click **"Sign in"** → Use GitHub account
3. Click **"New app"**

### 2b. Configure Deployment

**Repository:**
- Repository: `YOUR_USERNAME/Negotiation-Continuity-Experiment`
- Branch: `main`
- Main file path: `app.py`

**App URL:**
- Choose a custom URL (e.g., `negotiation-continuity`)
- Final URL will be: `https://YOUR_USERNAME-negotiation-continuity.streamlit.app`

### 2c. Add Secrets (IMPORTANT!)

Click **"Advanced settings"** → **"Secrets"**

Paste this (with your actual values):

```toml
# FalkorDB Cloud Configuration
USE_FALKORDB_CLOUD = "true"
FALKORDB_CLOUD_HOST = "r-6jissuruar.instance-ogljlqne2.hc-2uaqqpjgg.us-east-2.aws.f2e0a955bb84.cloud"
FALKORDB_CLOUD_PORT = "58039"
FALKORDB_CLOUD_PASSWORD = "k92vLdiURQd8"

# OpenAI (if using NL queries)
OPENAI_API_KEY = "your-openai-key"
```

**Why Secrets?**
- Keeps passwords out of GitHub (security!)
- Streamlit loads these as environment variables
- Same as `.env` file, but for cloud

### 2d. Deploy!

1. Click **"Deploy!"**
2. Wait 2-3 minutes for build
3. You'll see build logs
4. When done, your app is live!

---

## Step 3: Test Your Deployment

### 3a. Open Your App

URL will be: `https://YOUR_USERNAME-negotiation-continuity.streamlit.app`

### 3b. Verify It Works

**Test these features:**
1. ✅ Sidebar shows node counts (Clause: 112, etc.)
2. ✅ Natural Language Queries tab loads
3. ✅ Run query: "Show me all concessions" → Should return 2 results
4. ✅ Graph Visualization tab works
5. ✅ KPI Dashboard displays

### 3c. Troubleshooting

**If you see connection errors:**

1. Check Secrets are set correctly:
   - Go to app settings → Secrets
   - Verify all values match your `.env` file

2. Check FalkorDB Cloud is running:
   - Log into https://cloud.falkordb.cloud
   - Verify instance status is "Running"

3. Check build logs:
   - Click "Manage app" → "Logs"
   - Look for error messages

**Common issues:**
- `Connection refused` → Check cloud host/port in secrets
- `Authentication failed` → Check password in secrets
- `Module not found` → Check requirements.txt has all dependencies

---

## Step 4: Share with Your Boss!

### Option A: Send Direct Link

```
Subject: Negotiation Continuity System - Live Demo

Hi [Boss Name],

The Negotiation Continuity Knowledge Graph is now live!

🌐 Interactive Web App:
https://YOUR_USERNAME-negotiation-continuity.streamlit.app

Features:
• Natural language queries ("Show me all concessions")
• Interactive graph visualization
• Real-time KPI dashboards
• Full negotiation history across 4 contract versions

No installation needed - just click and explore!

Best,
[Your Name]
```

### Option B: Demo Together

1. Share screen on Zoom/Teams
2. Walk through the 4 tabs:
   - Natural Language Queries
   - Graph Visualization
   - KPI Dashboard
   - About
3. Run the key queries:
   - "Show me all concessions" → 2 results
   - "Track clause 1.1 history" → 4 versions

---

## Streamlit Cloud Features

**Free Tier Includes:**
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ Community support
- ✅ Auto-redeploy on git push
- ✅ Custom subdomains

**Your App:**
- Running 24/7
- Auto-updates when you push to GitHub
- Shareable URL
- No server management

---

## Updating Your App

**To make changes:**

1. Edit files locally
2. Test locally: `./launch_ui.sh`
3. Commit changes: `git commit -am "Update message"`
4. Push to GitHub: `git push`
5. Streamlit Cloud auto-redeploys (takes ~2 min)

**No manual redeployment needed!**

---

## Alternative: Local Only (If You Don't Want to Deploy Yet)

**Just share the FalkorDB Browser access:**
- URL: https://browser.falkordb.com
- Give them the connection details from SHARE_WITH_BOSS.md
- They can run queries directly

**Or run Streamlit locally and screen share:**
- Works great for 1-on-1 demos
- No cloud deployment needed
- Full control over environment

---

## Cost

**Streamlit Cloud:** FREE (public apps)
**FalkorDB Cloud:** FREE TIER (100 MB, enough for your data)
**Total:** $0/month

**If you need private apps later:**
- Streamlit Cloud Pro: $20/month per editor
- Or self-host on AWS/GCP/Azure

---

## Security Notes

**Public vs Private:**
- Streamlit Cloud free tier = **Public apps** (anyone with URL can access)
- If you need authentication, upgrade to Streamlit Cloud Pro
- FalkorDB credentials are stored in Secrets (not visible in code)

**For now:**
- App is public but obscure (hard-to-guess URL)
- Only people you share URL with will find it
- Good enough for demos and pilots

---

## Next Steps After Deployment

### Immediate:
1. ✅ Test the deployed app
2. ✅ Share URL with stakeholders
3. ✅ Gather feedback

### Short Term:
1. Add authentication (if needed)
2. Custom domain (if needed)
3. Add more synthetic data
4. Build custom dashboards

### Long Term:
1. Integrate with real contract systems
2. Add AI-powered clause analysis
3. Roll out to pilot team
4. Scale to production

---

## Support

**Streamlit Cloud Issues:**
- Docs: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Forum: https://discuss.streamlit.io/
- Status: https://streamlit.statuspage.io/

**Your App Issues:**
- Check build logs in Streamlit Cloud dashboard
- Test locally first with `./launch_ui.sh`
- Review SHARE_WITH_BOSS.md for troubleshooting

---

**Questions?** This guide covers everything you need to deploy. Follow the steps in order and you'll be live in 10 minutes!
