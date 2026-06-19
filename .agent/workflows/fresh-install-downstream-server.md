---
description: Seamlessly clones the Powercord framework into a new downstream deployment, provisions the container environment, and natively configures core extensions.
---

# Fresh Install Downstream Deployment

This workflow sets up a fresh downstream deployment from the upstream core framework. 

## Steps

1. **Deploy Target:** Clone the upstream to the downstream directory, stashing and restoring configuration/db files.
If updating an existing target directory, completely wipe it first to avoid artifacts. We preserve `.sql`, `.dump`, and `.env` files in a temporary stash before wiping.
```bash
UPSTREAM_DIR="../powercord"
TARGET_DIR="../powercord-downstream-server"
TEMP_STASH="../stash-temp"

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

# Clone upstream to downstream directory
cd "$UPSTREAM_DIR"
just init-target "$TARGET_DIR"

# Restore preserved files
if [ -d "$TEMP_STASH" ]; then
    cp -r "$TEMP_STASH"/* "$TARGET_DIR/"
    rm -rf "$TEMP_STASH"
fi
```

2. **Migrate Secrets:** Copy `.env` / `.env.prod` files from the upstream repository if they do not already exist in the downstream folder.
```bash
UPSTREAM_DIR="../powercord"
TARGET_DIR="../powercord-downstream-server"

if [ ! -f "$TARGET_DIR/.env" ]; then
    cp "$UPSTREAM_DIR/.env" "$TARGET_DIR/.env"
fi
if [ ! -f "$TARGET_DIR/.env.prod" ]; then
    cp "$UPSTREAM_DIR/.env.prod" "$TARGET_DIR/.env.prod"
fi
```

3. **Dependency Seeding & Host Database Setup:** Seed the dependencies by running `just install` and prepare the host database setup using `just db-upgrade` on the host.
```bash
cd "../powercord-downstream-server"
just install
just db-upgrade
```

4. **Extension Injection:** On the host, natively install domain-specific endpoints and capabilities.
```bash
cd "../powercord-downstream-server"
just ext-install "../powercord-extensions/midi_library"
just ext-install "../powercord-extensions/honeypot"
```

5. **Containerization:** Spin up the target containers, ensuring no port conflicts on port 5433.
* **Port Conflict Pre-Check & Stop Host DB**: Before starting, verify that port `5433` is free and stop the host database container if it is running:
  ```bash
  docker ps
  # If powercord-pg-dev is running, stop it:
  docker stop powercord-pg-dev
  ```
* **Build and Start**: Build the containerized target environment. Run the rebuild command exactly once:
  ```bash
  cd "../powercord-downstream-server"
  just rebuild-target
  ```
* **Compose DB Liveness Check**: Wait for the compose database to be fully ready using the built-in recipe:
  ```bash
  just _wait-for-compose-db
  ```

6. **Database Restore:** If a `powercord-export.sql` file was preserved, import it to restore the database state.
```bash
cd "../powercord-downstream-server"
if [ -f "powercord-export.sql" ]; then
    just db-import "powercord-export.sql"
fi
```

7. **Validation:** Ensure clean startup via `docker compose logs`. Verify that Uvicorn logs `Application startup complete.` and extension components mounted natively.
```bash
cd "../powercord-downstream-server"
docker compose logs --tail 30 app
```

---

## Testing First-Load & Fresh Build Logic

When validating features that run on first-load or rely on a "fresh database" (for example, the automatic provisioning of default widgets when a guild dashboard is opened for the first time), **pre-existing database state will bypass this logic**. 

To properly test these behaviors:
1. You must drop the database volume to clear any lingering layout or widget settings.
2. In the target directory (e.g. `../powercord-downstream-server`), run:
   ```bash
   docker compose down -v
   # Execute the containerization command as shown in Step 5
   ```
3. Access the dashboard. Because the database is empty, the first-load widget provisioning logic will execute, enabling the default widgets configured in `extension.json`.