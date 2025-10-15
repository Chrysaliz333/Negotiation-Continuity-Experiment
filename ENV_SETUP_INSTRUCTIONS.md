# Environment Setup Instructions

## Step 1: Start Docker Desktop

Before proceeding, ensure Docker Desktop is running:

1. Open Docker Desktop application
2. Wait for Docker to fully start (Docker icon in menu bar)
3. Verify: `docker ps` should work without errors

---

## Step 2: Start FalkorDB

Run the following command to start FalkorDB:

```bash
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  -v falkordb-data:/data \
  falkordb/falkordb:latest
```

**Verify it's running:**
```bash
docker ps | grep falkordb
```

**Test connection:**
```bash
docker exec -it falkordb redis-cli PING
```
Expected response: `PONG`

---

## Step 3: Configure .env File

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
# Required
OPENAI_API_KEY=sk-proj-...YOUR_KEY_HERE...

# FalkorDB (defaults should work)
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
GRAPHITI_TELEMETRY_ENABLED=false
SEMAPHORE_LIMIT=10

# Misc
LOG_LEVEL=INFO
```

**Get your OpenAI API key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and paste into `.env`

---

## Step 4: Test Connectivity

Test FalkorDB connection:

```bash
source venv/bin/activate
python scripts/test_falkordb_connection.py
```

Expected output:
```
✅ FalkorDB connection successful!
PONG response received
Graph 'test_graph' created successfully
```

---

## Step 5: Verify Synthetic Data

Check that synthetic data exists:

```bash
ls -lh data/ground_truth/synthetic/
```

You should see 12 JSON files (3 matters × 4 versions each).

---

## Troubleshooting

### Docker not running
- **Error**: `Cannot connect to the Docker daemon`
- **Fix**: Start Docker Desktop app, wait for it to fully start

### Port 6379 already in use
- **Error**: `port is already allocated`
- **Fix**: Either stop the conflicting service or use a different port:
  ```bash
  docker run -d --name falkordb -p 6380:6379 -p 3001:3000 ...
  # Then update .env: FALKORDB_PORT=6380
  ```

### OpenAI API key issues
- **Error**: `AuthenticationError` or `401 Unauthorized`
- **Fix**:
  1. Verify key in .env starts with `sk-proj-`
  2. Check key is valid at https://platform.openai.com/api-keys
  3. Ensure you have billing enabled

### FalkorDB connection refused
- **Check**: Is container running? `docker ps | grep falkordb`
- **Check**: Is port exposed? `docker port falkordb`
- **Restart**: `docker restart falkordb`

---

## Next Steps

Once all tests pass, you're ready to:

1. Load synthetic data into Graphiti
2. Run ingestion pipeline
3. Execute test queries
4. Begin KPI measurements

**Current Status**: Environment setup complete ✅
**Next**: Run `python scripts/ingest/load_graphiti.py --dry-run` to test ingestion logic
