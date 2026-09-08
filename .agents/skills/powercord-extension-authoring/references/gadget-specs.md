# Extension Gadgets Specification

Powercord extensions compose functionality through modular "gadgets".

---

## 1. Gadget Types

1. **Cogs (`cog.py`)**: Nextcord commands, slash commands, event listeners (`@commands.Cog.listener()`), and guild state handlers.
2. **Sprockets (`sprocket.py`)**: FastAPI `APIRouter` endpoints returning JSON for companion client consumption. Secured with `api_scope_required()`.
3. **Widgets (`widget.py`)**: FastHTML components rendered inside dashboard grids. Must adhere to prefix naming (`admin_`, `guild_admin_`).
4. **Routes (`routes.py`)**: Full-page FastHTML routes registered via `register_routes(rt)`. Public pages declare `PUBLIC_PATHS`.
5. **Blueprints (`blueprint.py`)**: Shared SQLModel/SQLAlchemy models and business logic.
6. **Scheduled Actions (`actions.py`)**: Background cron and interval jobs discovered and registered via `get_scheduled_actions() -> list[ScheduledAction]` or `SCHEDULED_ACTIONS = [...]`.
   - **Daily Log Scan Pattern**: Fast, lightweight cron (`{"hour": 4, "minute": 0}`) scanning recent unresolved errors with auto-repair.
   - **Monthly Full Audit Pattern**: Comprehensive deep catalog scan (`{"day": 1, "hour": 3, "minute": 30}`) comparing database records against storage objects with repair and pruning.

---

## 2. Discord Bot Interaction, Status Cards & Channel Scanning Best Practices

When authoring Discord cogs that process long-running jobs, historical message sweeps, or bulk archives:

### 2.1 Dynamic Response Granularity & Anti-Spam
- **Single File Drops**: Deliver rich visual cards and embeds with full metrics, spectrogram piano-rolls, and track instrumentation.
- **Bulk Uploads & Archives**: Suppress individual file embeds, PNG attachments, and per-track stats. Return a condensed summary card (`X files imported, Y duplicates, Z failed`) with top-5 item previews and tidy count summaries (`...and X more items added to the collection!`).

### 2.2 Status Card Stabilization & Heartbeat Feedback
- **Fixed-Structure Status Cards**: Standardize status updates on a fixed 4–5 line card hierarchy (Header with heartbeat pulse, Status, Messages Scanned, Items Imported, Batch Progress, Elapsed Time). Never alternate between 1-line notices and multi-line blocks, which causes Discord chat UI height oscillation ("jumpiness").
- **Live Heartbeat Pulse**: Update elapsed time and cycle heartbeat icons (`💓`, `💗`, `💖`) every 2.5s to provide continuous visual proof of process liveness during long-running background tasks.
- **Terminal State Heartbeat Dismissal**: Suppress pulsing heartbeat text (`· *Heartbeat active*`) once an operation enters a terminal state (`Complete`, `Paused`, `Error`), retaining pure elapsed time summary.

### 2.3 High-Throughput Sweeps & Ingestion Parallelism
- **Cooperative Event Loop Yielding**: Yield to the event loop periodically (`await asyncio.sleep(0)` every 100 messages) during historical sweeps to prevent gateway heartbeat starvation and WebSocket disconnects.
- **Discord Character Limit Clamping**: Hard-clamp all Discord status edits to $\le 1,850$ characters to avoid `400 Bad Request (50035)` exceptions that freeze status messaging.
- **Archive Sub-Progress Reporting**: Provide real-time item-level progress callbacks (`archive.zip (cur/tot: fname)`) during extraction so operators have visibility into archive contents.
- **Fast-Path Bulk Checksum Deduplication**: Compute SHA-256 hashes in memory up-front and query existing records in a single SQL query (`select(Model).where(Model.checksum.in_(...))`). Instantly bypass known tracks in ~5ms before expensive parsing or remote cloud storage uploads.
- **Worker Throttling**: Throttle or pause background generation/repair workers during active real-time sweeps (`_is_scan_active()`) to dedicate 100% CPU and network bandwidth to the user-visible scan.
- **Decoupled Derived Asset Ingestion**: Single uploads render visual assets synchronously; bulk sweeps and multi-file archives defer visual asset generation to an asynchronous repair queue (`generate_png=False`), boosting ingestion throughput by 25x–50x.
