---
description: Seamlessly clones the Powercord framework into a new downstream deployment, provisions the container environment, and natively configures core extensions.
---

# Fresh Install Downstream Deployment

This workflow sets up a fresh downstream deployment from the upstream core framework. 

## Pre-requisite: Teardown
If updating an existing target directory, completely wipe it first to avoid artifacts. We preserve `.sql`, `.dump`, and `.env` files in a temporary stash before wiping.
```bash
TARGET_DIR="/path/to/target-project"
TEMP_STASH="/path/to/stash-temp"

# Stop running containers and destroy the old database volume
if [ -d "$TARGET_DIR" ]; then
    cd "$TARGET_DIR"
    if [ -f "docker-compose.yml" ]; then 
        docker compose down -v 
    fi
    cd ..
    
    # Stash files to preserve
    mkdir -p "$TEMP_STASH"
    find "$TARGET_DIR" -maxdepth 1 -type f \( -name "*.sql" -o -name "*.dump" -o -name ".env*" \) -exec cp {} "$TEMP_STASH/" \;
    
    rm -rf "$TARGET_DIR"
fi
```

## Steps

1. **Deploy Target:** Navigate to the upstream `powercord` repository and execute `init-target`. This safely creates a clone and disables upstream pushes to protect the core framework.
```bash
UPSTREAM_DIR="/path/to/powercord"
TARGET_DIR="/path/to/target-project"
TEMP_STASH="/path/to/stash-temp"

cd "$UPSTREAM_DIR"
just init-target "$TARGET_DIR"

# Restore preserved files
if [ -d "$TEMP_STASH" ]; then
    cp -r "$TEMP_STASH"/* "$TARGET_DIR/"
    rm -rf "$TEMP_STASH"
fi
```

2. **Migrate Secrets:** Copy your internal security profiles.
```bash
UPSTREAM_DIR="/path/to/powercord"
TARGET_DIR="/path/to/target-project"

if [ ! -f "$TARGET_DIR/.env" ]; then
    cp "$UPSTREAM_DIR/.env" "$TARGET_DIR/.env"
fi
if [ ! -f "$TARGET_DIR/.env.prod" ]; then
    cp "$UPSTREAM_DIR/.env.prod" "$TARGET_DIR/.env.prod"
fi
```

3. **Dependency Seeding:** Install Python requirements in the new target to generate the `.venv`.
```bash
cd "/path/to/target-project"
just install
```

4. **Containerization:** Spin up the base container and database.
   * **Port Conflict Pre-Check**: Before starting, verify that port `5433` is free:
     ```bash
     docker ps
     # If powercord-pg-dev is running, stop it:
     docker stop powercord-pg-dev
     ```
   * Spin up:
     ```bash
     cd "/path/to/target-project"
     just rebuild-target
     ```

5. **Extension Injection:** Natively install domain-specific endpoints and capabilities.
   * **Postgres Liveness Check**: Ensure PostgreSQL is fully accepting connections before running the installation script. Verify container logs show database startup complete, or run:
     ```bash
     until docker compose exec app pg_isready -h localhost -U postgres; do sleep 1; done
     ```
   * Install:
     ```bash
     cd "/path/to/target-project"
     just ext-install "../powercord-extensions/midi_library"
     just ext-install "../powercord-extensions/honeypot"
     # If the migration fails with a network error during install, run:
     just db-upgrade
     ```

6. **Image Bake-in:** Execute a final rebuild to inject extension artifacts into the persistent Docker image.
   * Rebuild:
     ```bash
     cd "/path/to/target-project"
     just rebuild-target
     ```

7. **Database Restore:** If a `powercord-export.sql` file was preserved, import it to restore the database state.
```bash
cd "/path/to/target-project"
if [ -f "powercord-export.sql" ]; then
    just db-import "powercord-export.sql"
fi
```

8. **Validation:** Ensure clean startup via `docker compose logs`. Verify that Uvicorn logs `Application startup complete.` and extension components mounted natively.
```bash
cd "/path/to/target-project"
docker compose logs --tail 30 app
```

---

## Testing First-Load & Fresh Build Logic

When validating features that run on first-load or rely on a "fresh database" (for example, the automatic provisioning of default widgets when a guild dashboard is opened for the first time), **pre-existing database state will bypass this logic**. 

To properly test these behaviors:
1. You must drop the database volume to clear any lingering layout or widget settings.
2. In the target directory (e.g. `powercord-downstream-server`), run:
   ```bash
   docker compose down -v
   just rebuild-target
   ```
3. Access the dashboard. Because the database is empty, the first-load widget provisioning logic will execute, enabling the default widgets configured in `extension.json`.