# Setup Instructions

**Get the Negotiation Continuity System running on any machine in 5 minutes**

---

## Prerequisites

- **macOS**, **Linux**, or **Windows** with WSL
- **Docker Desktop** installed ([download here](https://www.docker.com/products/docker-desktop))
- **Python 3.9+** installed

---

## Quick Setup (5 minutes)

### Step 1: Extract the files
```bash
unzip Negotiation-Continuity-Demo.zip
cd Negotiation-Continuity-Demo
```

(Or if using git: `git clone <repo-url>` and `cd` into directory)

---

### Step 2: Start Docker
**Open Docker Desktop** - it must be running for FalkorDB to work.

Verify Docker is running:
```bash
docker ps
```

Should show running containers (or empty list if none running yet).

---

### Step 3: Start FalkorDB
```bash
docker run -d --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  -v falkordb-data:/data \
  falkordb/falkordb:latest
```

**What this does:**
- Downloads FalkorDB image (first time only)
- Starts FalkorDB on ports 6379 (database) and 3000 (browser UI)
- Creates persistent volume for data

**Verify it's running:**
```bash
docker ps | grep falkordb
```

Should show `falkordb` container running.

**Test connectivity:**
```bash
docker exec falkordb redis-cli PING
```

Should return: `PONG`

---

### Step 4: Create Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 5: Install dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `falkordb` - Graph database client
- `redis` - Database connectivity
- `pydantic` - Data validation
- `python-dotenv` - Environment variables

Should take ~30 seconds.

---

### Step 6: Run the demo!

**Automated demo (recommended first run):**
```bash
./demo.sh
```

Press ENTER to advance through each question.

**Interactive mode:**
```bash
python scripts/nl_query.py
```

Then ask questions like:
- `Show me all concessions`
- `Find liability clauses`
- `What did we agree to in round 2?`

Type `quit` to exit.

**Single query mode:**
```bash
python scripts/nl_query.py "Show me all concessions"
```

---

## 🌐 Visual Graph Browser

**Open in your web browser:**
```
http://localhost:3000
```

You'll see the FalkorDB visual interface where you can:
- Explore the graph visually
- Click on nodes to see relationships
- Run Cypher queries
- Browse all 206 nodes and 73 relationships

**If it asks for login:** Just click "Connect" (no credentials needed for local instance)

---

## ✅ Verify Everything Works

**Test 1: Check database**
```bash
python -c "
from falkordb import FalkorDB
db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('negotiation_continuity')
result = graph.query('MATCH (n) RETURN COUNT(n)')
print(f'✅ Nodes in database: {result.result_set[0][0]}')
"
```

Should show: `✅ Nodes in database: 206`

**Test 2: Run a query**
```bash
python scripts/nl_query.py "How many clauses are there?"
```

Should show:
```
Matters: 12
Parties: 24
Clauses: 112
Recommendations: 28
Decisions: 28
Concessions: 2
```

**Test 3: Measure KPIs**
```bash
python scripts/measure_kpis.py
```

Should show 4 of 5 KPIs passing.

---

## 📚 Documentation

Once setup is complete, read these files:

- **QUICK_START.md** - How to use the system
- **BOSS_DEMO_GUIDE.md** - Demo script and questions
- **KPI_ANALYSIS.md** - Performance validation details
- **README.md** - Project overview

---

## 🔧 Troubleshooting

### Issue: "command not found: python"
**Solution:** Try `python3` instead:
```bash
python3 scripts/nl_query.py
```

Or create an alias:
```bash
alias python=python3
```

---

### Issue: "Cannot connect to Docker daemon"
**Solution:** Make sure Docker Desktop is running:
- Open Docker Desktop application
- Wait for it to fully start (whale icon in menu bar)
- Try again

---

### Issue: "Permission denied: ./demo.sh"
**Solution:** Make it executable:
```bash
chmod +x demo.sh
```

---

### Issue: FalkorDB container not running
**Check status:**
```bash
docker ps -a | grep falkordb
```

**If stopped, start it:**
```bash
docker start falkordb
```

**If doesn't exist, create it:**
```bash
docker run -d --name falkordb -p 6379:6379 -p 3000:3000 \
  -v falkordb-data:/data falkordb/falkordb:latest
```

---

### Issue: "ModuleNotFoundError: No module named 'falkordb'"
**Solution:** Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate      # On Windows
```

Then install dependencies:
```bash
pip install -r requirements.txt
```

---

### Issue: Port 6379 or 3000 already in use
**Solution:** Stop other services using those ports, or change ports:
```bash
# Use different ports
docker run -d --name falkordb -p 6380:6379 -p 3001:3000 \
  -v falkordb-data:/data falkordb/falkordb:latest

# Then update .env file:
# FALKORDB_PORT=6380
```

---

### Issue: Browser shows blank page at localhost:3000
**Solution:**
1. Wait 10 seconds for FalkorDB to fully start
2. Refresh the page
3. Check container logs:
   ```bash
   docker logs falkordb
   ```

---

## 🔑 Optional: OpenAI API Key

The system works without an OpenAI API key for all current features.

**If you want to enable future semantic search features:**

1. Get API key from: https://platform.openai.com/api-keys
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your key:
   ```bash
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

---

## 🧹 Cleanup (Optional)

**To remove everything and start fresh:**

```bash
# Stop and remove FalkorDB container
docker stop falkordb
docker rm falkordb

# Remove data volume (warning: deletes all data)
docker volume rm falkordb-data

# Remove Python virtual environment
deactivate  # If activated
rm -rf venv

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 🚀 Quick Command Reference

```bash
# Start everything
docker start falkordb
source venv/bin/activate

# Run demo
./demo.sh

# Interactive queries
python scripts/nl_query.py

# Measure performance
python scripts/measure_kpis.py

# Test queries
python scripts/test_queries.py

# Open browser
open http://localhost:3000

# Stop everything
docker stop falkordb
deactivate
```

---

## 📞 System Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Docker Desktop

**Recommended:**
- 8GB RAM
- 5GB free disk space
- Modern web browser (Chrome, Firefox, Safari)

**Operating Systems Tested:**
- ✅ macOS 12+ (Monterey and later)
- ✅ Ubuntu 20.04+
- ✅ Windows 10/11 with WSL2

---

## ✅ Success Checklist

After setup, you should be able to:
- [ ] Docker is running: `docker ps | grep falkordb`
- [ ] Database responds: `docker exec falkordb redis-cli PING` returns `PONG`
- [ ] Python works: `python scripts/nl_query.py "How many clauses are there?"`
- [ ] Browser opens: http://localhost:3000 shows FalkorDB UI
- [ ] Demo runs: `./demo.sh` shows all questions
- [ ] 206 nodes in database
- [ ] All queries return results in < 1 second

---

## 🎉 You're Ready!

The system is fully operational. Next steps:

1. **Try the demo**: `./demo.sh`
2. **Read the guide**: `QUICK_START.md`
3. **Explore queries**: `python scripts/nl_query.py`
4. **Check performance**: `python scripts/measure_kpis.py`

Questions? See **QUICK_START.md** or run `python scripts/nl_query.py` and type `help`.

Enjoy! 🚀
