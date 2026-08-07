# Development & Testing Guide

Quick reference for common tasks while developing.

---

## Starting & Stopping

### Start everything
```bash
docker compose up
```
Runs both db and api. Watch logs scroll by.

### Start and rebuild (after dependency changes)
```bash
docker compose up --build
```

### Start in background
```bash
docker compose up -d
```
Services run in background. You get your terminal back.

### Stop everything
```bash
docker compose down
```
Stops containers. Data persists (db-data volume remains).

### Stop and remove data
```bash
docker compose down -v
```
Stops containers AND deletes the database volume. Fresh start next time.

---

## Logs

### See logs from everything
```bash
docker compose logs
```
Shows all past logs, then exits.

### Follow logs (live, like tail -f)
```bash
docker compose logs -f
```
Streams logs in real-time. Press Ctrl+C to stop.

### Logs from just one service
```bash
docker compose logs api
docker compose logs db
```

### Follow just the api
```bash
docker compose logs -f api
```

### Last 50 lines of api logs
```bash
docker compose logs --tail=50 api
```

---

## Checking Status

### See if containers are running
```bash
docker compose ps
```

Shows:
```
NAME             IMAGE              STATUS
verdict-db-1     postgres:16        Up X seconds (healthy)
verdict-api-1    verdict-api        Up X seconds
```

### Check if db is healthy
```bash
docker compose ps db
```
Look for `(healthy)` in the STATUS column.

---

## Database Access

### Connect to postgres from host
```bash
docker compose exec db psql -U verdict -d verdict
```

Once connected, you can run SQL:
```sql
\dt              -- list tables
SELECT * FROM users;
SELECT * FROM games;
\q              -- quit
```

### Quick query (one-shot, no interactive shell)
```bash
docker compose exec db psql -U verdict -d verdict -c "SELECT * FROM users;"
```

### Check what tables exist
```bash
docker compose exec db psql -U verdict -d verdict -c "\dt"
```

---

## Running Migrations

### Run pending migrations
```bash
docker compose run --rm api alembic upgrade head
```

### See migration status
```bash
docker compose run --rm api alembic current
```

### Create a new migration (after changing models)
```bash
docker compose run --rm api alembic revision --autogenerate -m "description of change"
```

---

## Testing API

### Check Swagger UI loads
```bash
curl -s http://127.0.0.1:8000/docs | head -5
```
Should return HTML.

### Check OpenAPI schema
```bash
curl -s http://127.0.0.1:8000/openapi.json | jq '.info.title'
```
Should return `"Verdict"`.

### Hit any endpoint (example: GET /games)
```bash
curl -s http://127.0.0.1:8000/games \
  -H "Authorization: Bearer <user-uuid>"
```

---

## Debugging

### See all running containers
```bash
docker ps
```

### Inspect a container
```bash
docker inspect verdict-api
```
Shows config, environment variables, mounts, etc.

### Get the container ID for a service
```bash
docker compose ps -q api
```

### Run a command inside a running container
```bash
docker compose exec api python -m src.cli.run --help
```

### Open a shell inside the api container
```bash
docker compose exec api /bin/bash
```
Then you're inside; can run Python, check files, etc. Type `exit` to leave.

### Open a shell in the db container
```bash
docker compose exec db /bin/bash
```

---

## Rebuilding

### Rebuild just the api image
```bash
docker compose build api
```

### Rebuild and restart
```bash
docker compose up --build -d
```

### Clean rebuild (ignore cache)
```bash
docker compose build api --no-cache
docker compose up -d
```

---

## Common Workflows

### "I changed models and want to test"
```bash
# Create migration
docker compose run --rm api alembic revision --autogenerate -m "my change"

# Check the migration file looks right
cat api/alembic/versions/[latest-file].py

# Run it
docker compose run --rm api alembic upgrade head

# Restart api to pick up changes
docker compose restart api
```

### "I want a fresh database"
```bash
docker compose down -v
docker compose up --build
```

### "Everything is broken, start over"
```bash
docker compose down -v
docker system prune -f
docker compose up --build
```

### "Database connection refused"
```bash
# Make sure db is running
docker compose ps db

# If it says "Exited", restart it
docker compose up db -d

# Wait for healthy
sleep 10

# Check again
docker compose ps db
```

### "I need to see what's in the database"
```bash
docker compose exec db psql -U verdict -d verdict

# Then in psql:
SELECT * FROM users \g
SELECT * FROM games \g
SELECT * FROM events LIMIT 5 \g
\q
```

### "App won't start, need to see why"
```bash
docker compose up --build
```
Watch the output. Look for red errors.

Or if it's running in background:
```bash
docker compose logs -f api
```

---

## Environment Variables

### View current env vars in running container
```bash
docker compose exec api env | grep DATABASE
```

### Check if .env was loaded
```bash
docker compose exec api env | grep POSTGRES
```

---

## File Access

### Copy a file from container to host
```bash
docker compose cp verdict-api:/app/src/app/models/db.py ./
```

### Copy from host to running container
```bash
docker compose cp ./myfile.py verdict-api:/app/
```

---

## Cleanup

### Remove stopped containers
```bash
docker compose rm
```

### Remove unused images
```bash
docker image prune -f
```

### Remove everything (containers, images, volumes)
```bash
docker compose down -v
docker system prune -a -f
```
Use with caution — deletes everything.

---

## Quick Reference: Common Issues

| Problem | Command |
|---------|---------|
| "Can't connect to db" | `docker compose ps db` (check if healthy) |
| "Logs scroll too fast" | `docker compose logs --tail=50 -f api` |
| "Want to see one SQL query result" | `docker compose exec db psql -U verdict -d verdict -c "SELECT * FROM users;"` |
| "Changed code, not seeing changes" | `docker compose restart api` |
| "Changed dependencies (pyproject.toml)" | `docker compose up --build` |
| "Changed database schema" | `alembic revision --autogenerate -m "..."` then `alembic upgrade head` |
| "Want fresh database" | `docker compose down -v && docker compose up --build` |
| "App won't start" | `docker compose logs -f api` (watch for errors) |

---

## Notes

- `.env` file is **not committed** to git (add to `.gitignore`)
- Database data persists in `db-data` volume even after `docker compose down`
- Logs are not persisted; they're only in memory while containers run
- Migrations are stored in `api/alembic/versions/`

---

Last updated: Aug 6, 2026