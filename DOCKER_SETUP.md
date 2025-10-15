# Docker Setup Instructions

## Start Docker Desktop

Before proceeding with FalkorDB setup, you need to start Docker Desktop:

1. **Open Docker Desktop application** (located in Applications folder)
2. **Wait for Docker to start** (you'll see the Docker icon in the menu bar)
3. **Verify Docker is running**: Open Terminal and run `docker ps`

---

## FalkorDB Quick Start

Once Docker is running, execute these commands:

### 1. Pull and Start FalkorDB Container

```bash
docker run -d \
  --name falkordb \
  -p 6379:6379 \
  -p 3000:3000 \
  -v falkordb-data:/data \
  falkordb/falkordb:latest
```

**What this does:**
- `-d`: Run in detached mode (background)
- `--name falkordb`: Names the container "falkordb"
- `-p 6379:6379`: Exposes FalkorDB port (Redis-compatible)
- `-p 3000:3000`: Exposes FalkorDB Browser UI
- `-v falkordb-data:/data`: Persists data to named volume
- `falkordb/falkordb:latest`: Uses latest FalkorDB image

### 2. Verify Container is Running

```bash
docker ps | grep falkordb
```

You should see output like:
```
CONTAINER ID   IMAGE                     STATUS         PORTS
abc123def456   falkordb/falkordb:latest  Up 10 seconds  0.0.0.0:6379->6379/tcp, 0.0.0.0:3000->3000/tcp
```

### 3. Test Connection

```bash
docker exec -it falkordb redis-cli PING
```

Expected response: `PONG`

### 4. Access FalkorDB Browser (Optional)

Open in web browser: http://localhost:3000

This provides a visual interface for exploring the graph database.

---

## Useful Docker Commands

### Check Container Status
```bash
docker ps -a --filter name=falkordb
```

### View Logs
```bash
docker logs falkordb
```

### Stop Container
```bash
docker stop falkordb
```

### Start Existing Container
```bash
docker start falkordb
```

### Remove Container (Warning: Deletes data if volume not used)
```bash
docker stop falkordb
docker rm falkordb
```

### Remove Container AND Volume (Complete reset)
```bash
docker stop falkordb
docker rm falkordb
docker volume rm falkordb-data
```

---

## Connection Details for .env

Once FalkorDB is running, use these connection settings:

```bash
# FalkorDB Connection
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_GRAPH_NAME=negotiation_continuity

# Or full connection string
FALKORDB_URL=redis://localhost:6379
```

---

## Troubleshooting

### "Cannot connect to Docker daemon"
- Start Docker Desktop application
- Wait for Docker icon to appear in menu bar
- Try command again

### "Port already in use"
If port 6379 is already in use by another service:

```bash
# Use different port
docker run -d \
  --name falkordb \
  -p 6380:6379 \
  -p 3001:3000 \
  -v falkordb-data:/data \
  falkordb/falkordb:latest

# Update .env with new port
FALKORDB_PORT=6380
```

### "Container name already in use"
```bash
# Remove existing container
docker rm falkordb

# Or use different name
docker run -d --name falkordb-negotiation ...
```

---

## Next Steps After Docker Setup

Once FalkorDB is running, proceed with:

1. Install Python dependencies: `source venv/bin/activate && pip install graphiti-core[falkordb]`
2. Configure `.env` file with OpenAI API key
3. Test connectivity with `scripts/test_falkordb_connection.py`
4. Begin ingestion with synthetic data

---

**Status**: Waiting for Docker Desktop to start
**Next Command**: `docker run -d --name falkordb -p 6379:6379 -p 3000:3000 -v falkordb-data:/data falkordb/falkordb:latest`
