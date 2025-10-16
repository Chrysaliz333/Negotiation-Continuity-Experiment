# Quick FalkorDB Cloud Setup - 5 Minutes

**Get your Knowledge Graph online and shareable in 5 minutes!**

---

## Step 1: Get Your Cloud Credentials (2 minutes)

1. **Log into FalkorDB Cloud**: https://cloud.falkordb.cloud

2. **Create New Database**:
   - Click "Create Database"
   - Name: `negotiation-continuity`
   - Region: Choose closest to you
   - Plan: Free tier is fine for demos

3. **Copy Your Credentials**:
   After creation, you'll see:
   ```
   Host: xxx-xxx.falkordb.cloud
   Port: 6379
   Password: [your-password]
   ```

---

## Step 2: Add Credentials to .env (30 seconds)

Open your `.env` file and add:

```bash
# FalkorDB Cloud Configuration
USE_FALKORDB_CLOUD=false  # Keep false for now
FALKORDB_CLOUD_HOST=your-instance.falkordb.cloud
FALKORDB_CLOUD_PORT=6379
FALKORDB_CLOUD_PASSWORD=your-actual-password-here
```

**Replace** `your-instance.falkordb.cloud` and `your-actual-password-here` with your actual values!

---

## Step 3: Upload Your Data (2 minutes)

```bash
# Make sure local FalkorDB is running
docker start falkordb

# Run the export script
python3 scripts/export_to_cloud.py
```

**The script will:**
1. ✅ Connect to your local FalkorDB
2. ✅ Connect to FalkorDB Cloud
3. ✅ Ask if you want to clear existing cloud data (say 'y' for first upload)
4. ✅ Copy all 206 nodes
5. ✅ Copy all 73 relationships
6. ✅ Verify the data

**Expected output:**
```
================================================================================
FALKORDB CLOUD EXPORT
================================================================================
📡 Connecting to local FalkorDB...
✅ Connected to local FalkorDB
   Graph: negotiation_continuity
   Nodes: 206

📡 Connecting to FalkorDB Cloud...
✅ Connected to FalkorDB Cloud

⚠️  Clear existing data in cloud? (y/N): y
🗑️  Clearing cloud graph...
✅ Cloud graph cleared

📦 Copying nodes to cloud...
  Copying Matter nodes... ✅ 12 nodes
  Copying Party nodes... ✅ 24 nodes
  Copying Clause nodes... ✅ 112 nodes
  Copying Recommendation nodes... ✅ 28 nodes
  Copying Decision nodes... ✅ 28 nodes
  Copying Concession nodes... ✅ 2 nodes

✅ Total nodes copied: 206

🔗 Copying relationships to cloud...
  Copying HAS_RECOMMENDATION relationships... ✅ 28 relationships
  Copying HAS_DECISION relationships... ✅ 28 relationships
  Copying RESULTED_IN_CONCESSION relationships... ✅ 2 relationships

✅ Total relationships copied: 58

🔍 Verifying cloud data...
✅ Verification complete!

================================================================================
✅ EXPORT COMPLETE!
================================================================================
Your graph is now available in FalkorDB Cloud!
================================================================================
```

---

## Step 4: Test Cloud Access (30 seconds)

### Option A: Test from Terminal

```bash
python3 -c "
from falkordb import FalkorDB
import os
from dotenv import load_dotenv

load_dotenv()

db = FalkorDB(
    host=os.getenv('FALKORDB_CLOUD_HOST'),
    port=int(os.getenv('FALKORDB_CLOUD_PORT')),
    password=os.getenv('FALKORDB_CLOUD_PASSWORD'),
    ssl=True
)

graph = db.select_graph('negotiation_continuity')
result = graph.query('MATCH (n) RETURN COUNT(n)')
print(f'✅ Nodes in cloud: {result.result_set[0][0]}')
"
```

### Option B: Open Graph Browser

Open in your browser:
```
https://your-instance.falkordb.cloud:3000
```

Log in and explore the graph visually!

---

## Step 5: Share with Your Boss! (30 seconds)

### Option A: Share Graph Browser URL

Send them:
```
URL: https://your-instance.falkordb.cloud:3000
Graph Name: negotiation_continuity

They can:
• Browse the graph visually
• Run Cypher queries
• Export data
```

### Option B: Deploy Streamlit App to Cloud (Recommended!)

See **STREAMLIT_CLOUD_DEPLOY.md** for instructions on deploying your interactive UI to the cloud.

Once deployed, your boss just needs:
```
https://your-app.streamlit.app
```

No installation, no credentials, just click and explore!

---

## 🎉 You're Done!

Your Knowledge Graph is now:
- ✅ Hosted in the cloud
- ✅ Accessible from anywhere
- ✅ Shareable with a URL
- ✅ Available 24/7

**Total time: ~5 minutes**

---

## 🔄 Updating Cloud Data

Whenever you make changes locally, just run:

```bash
python3 scripts/export_to_cloud.py
```

It will sync your local changes to the cloud!

---

## 🆘 Troubleshooting

### "Failed to connect to FalkorDB Cloud"

**Check:**
1. Is your `.env` file filled out correctly?
2. Did you copy the password exactly (no extra spaces)?
3. Is your internet connection working?

**Try:**
```bash
# Test connection manually
python3 -c "
from falkordb import FalkorDB
db = FalkorDB(
    host='your-instance.falkordb.cloud',
    port=6379,
    password='your-password',
    ssl=True
)
db.ping()
print('✅ Connected!')
"
```

### "ModuleNotFoundError: No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Export seems stuck

- The export can take 1-2 minutes for 206 nodes
- Watch for the progress messages
- If it truly hangs, press Ctrl+C and try again

---

## 📧 Ready-to-Send Email Template

```
Subject: Negotiation Continuity System - Now Available Online

Hi [Boss Name],

The Negotiation Continuity Knowledge Graph is now live and accessible online!

🌐 Interactive Graph Browser:
https://your-instance.falkordb.cloud:3000

Graph Name: negotiation_continuity

You can:
• Explore the graph visually (206 nodes, 73 relationships)
• Run queries in Cypher or natural language
• See all concessions, decisions, and recommendations
• Track clauses across versions v1→v2→v3→v4

Try this query in the browser:
MATCH (c:Clause {clause_number: '1.1'})
RETURN c.version, c.title
ORDER BY c.version

This shows Clause 1.1 across all 4 versions - proving multi-session continuity!

Let me know if you'd like a quick walkthrough.

Best,
[Your Name]
```

---

## 🎯 Next Steps

1. ✅ **Cloud database is live** - You're done here!
2. 🚀 **Deploy Streamlit app** - See STREAMLIT_CLOUD_DEPLOY.md
3. 📧 **Share with stakeholders** - Use email template above
4. 🎬 **Schedule demo** - Show them the live system!

---

**Questions?** See FALKORDB_CLOUD_SETUP.md for detailed documentation.
