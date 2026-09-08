# Common Ecosystem Failure Patterns & Mitigations

---

## 1. Discord Client Slash Command Caching (Phantom Bugs)

* **Symptom**: Newly registered or updated slash commands do not appear in the Discord client UI after restarting the bot.
* **Root Cause**: The Discord client application caches guild and global commands aggressively.
* **Mitigation**: Advise the user to force-refresh their Discord client (`Ctrl+R` on desktop or reload app on mobile) before debugging command registration logic.

---

## 2. Alembic CLI Bootstrapping Conflicts

* **Symptom**: `alembic upgrade head` fails with `Can't locate revision`.
* **Root Cause**: The Alembic CLI resolves migration targets from `alembic.ini` on disk *before* executing `env.py`. Dynamically updating `version_locations` inside `env.py` is too late for the CLI runner.
* **Mitigation**: Always ensure `_update_alembic_ini()` is executed first (via `just db-upgrade` or in `start.sh`) so that `alembic.ini` contains all extension migration paths.

---

## 3. Downstream Extension Dependency Resets

* **Symptom**: Downstream tests fail with `ModuleNotFoundError` for an extension package after a git clean.
* **Root Cause**: Reconciling the downstream repository with `git checkout -- .` discards additions in `pyproject.toml` and `poetry.lock`.
* **Mitigation**: Rerun extension installation (`just ext-install ../path`) during the reconciliation workflow (`/reconcile-downstream-server`) to re-register missing dependencies.

---

## 4. Missing `devkit.just` DB Warnings

* **Symptom**: `just test` outputs `[devkit] powercord/devkit.just not found` and tests crash on DB connection.
* **Root Cause**: Running an extension outside the standard sibling directory layout.
* **Mitigation**: Export `POWERCORD_PATH=/path/to/powercord` so the extension resolves `devkit.just`.

---

## 5. Bot Internal API Lifecycle Crashes & Port Conflicts

* **Symptom**: FastHTML dashboard reports `Status: 🔴 Disconnected`, with `[Errno 98] address already in use` in `bot_crash.log`.
* **Root Cause**: Launching `start_bot_api` without task liveness checks during Discord gateway reconnections, or binding to static hardcoded `127.0.0.1:8001` URLs.
* **Mitigation**: Check `if not getattr(self, "bot_api_task", None) or self.bot_api_task.done():` in `on_ready()`, include a port retry backoff loop in `start_bot_api()`, and always route through `get_bot_api_url()`.

---

## 6. Raw Snowflake ID Leaks & False Positive Access State

* **Symptom**: Dashboard displays raw integers (e.g. `585161062266175521`) or displays "All available roles have been granted access" when only a small subset is assigned.
* **Root Cause**: Missing fallback to cached `DiscordRole` database table when bot is offline, and empty state evaluating unassigned items without verifying total discovered roles.
* **Mitigation**: Implement `_get_guild_roles` fallback to SQLModel tables, differentiate between 0 discovered roles vs 0 remaining unassigned roles, and provide manual Snowflake entry as a fallback.

---

## 7. Stale Discord Message Interactive Components (`view=None` vs Omitted)

* **Symptom**: Interactive UI buttons (e.g. `[ ⏸️ Pause Scan ]`) persist on Discord messages after a long-running process completes, pauses, or errors. Clicking the button raises *"This interaction failed / didn't respond in time"*.
* **Root Cause**: In message-editing helper wrappers (e.g. `_safe_status_edit`), using `if view is not None: kwargs["view"] = view` causes `view=None` to be omitted from the API call. In Nextcord / Discord API, omitting `view` preserves existing message components; removing components requires explicitly passing `view=None`.
* **Mitigation**: Define a sentinel default (e.g. `_VIEW_UNSET = object()`). Only omit `view` when unset; when `view is None` is explicitly passed, forward `view=None` to the Discord API to clear all interactive components.

---

## 8. Matplotlib Multi-Threading Crash in Worker Pools / Async Background Tasks

* **Symptom**: Server process abruptly aborts with SIGABRT or `Tcl_AsyncDelete: async handler deleted by the wrong thread` / `RuntimeError: main thread is not in main loop`.
* **Root Cause**: Matplotlib defaults to a GUI backend (`TkAgg`) on Linux. When figure generation and collection (`plt.close("all")`) occur in non-main worker threads (e.g. `ThreadPoolExecutor`, `asyncio.to_thread`), Tkinter crashes when deleting async handlers from non-main threads.
* **Mitigation**: Always configure `matplotlib.use("Agg")` *before* importing `matplotlib.pyplot` in any background worker, extension module, or multi-threaded service.

---

## 9. Derived Asset Database State Desynchronization

* **Symptom**: Database records report derived/cached assets as present (`has_png=True`), but files are missing on disk or in remote storage, producing broken UI tiles.
* **Root Cause**: Storing derived asset existence flags in the database creates split authority. Out-of-band file deletion or transfer desynchronizes database state.
* **Mitigation**: Physical storage is the single source of truth (`inv-omission-over-fallback-galleries`). Never add boolean asset columns to the database schema. Instead, detect missing assets at runtime (via query, web telemetry 404, or deferred scan import), omit the record from user views, log an unresolved `DataHealthError`, and enqueue an asynchronous repair job. Upon generation/upload, mark the error resolved to automatically restore visibility.

---

## 10. Trigram Search False Negatives on Compound Filenames

* **Symptom**: Keyword queries for known files (e.g. searching `"sabaton"` for `Sabaton_-_Carolus_Rex_-_Edit_by_Sesh.mid`) return 0 results.
* **Root Cause**: Whole-string `similarity(col, query) >= 0.3` divides matched trigrams by total unique trigrams across the entire string. When a short keyword is embedded in a long 40+ character filename, the similarity score falls below the 0.3 cutoff despite being an exact match.
* **Mitigation**: Use PostgreSQL's `word_similarity(query, col)` combined with `func.greatest` and substring ILIKE fallback:
  ```python
  word_sim = func.word_similarity(search_term, column)
  full_sim = func.similarity(column, search_term)
  stmt = stmt.where(or_(word_sim >= 0.3, column.ilike(f"%{search_term}%"))).order_by(
      func.greatest(word_sim, full_sim).desc()
  )
  ```

---

## 11. Scoring Metric False Positives on Multi-Track Unison/Layered Arrangements

* **Symptom**: High-quality, multi-instrument songs receive quality scores of 0/100 with 100% duplicate notes.
* **Root Cause**: Collecting note signatures `(pitch, start_time)` globally into a single set across all instruments. Layered instruments playing unison or octave-doubled parts (e.g. double-tracked rhythm guitars, layered orchestral strings) cause all subsequent tracks to be flagged as duplicates of the first track.
* **Mitigation**: Scope duplicate note signatures strictly per-instrument (`(inst_idx, pitch, start_time)`). Identical notes across distinct instruments represent valid unison/voicing, while duplicates on the *same* instrument track represent true errors.

---

## 12. Temporary Filename Prefix Mangling in Batch Ingestion

* **Symptom**: Database entries and web galleries display temporary UUIDs in filenames (e.g. `temp_8a1f_song.mid` instead of `song.mid`).
* **Root Cause**: Prepending UUID prefixes to downloaded filenames on disk to avoid concurrent collision, and passing the temporary file path's `.name` to database record creation.
* **Mitigation**: Isolate concurrent downloads into dedicated temporary subdirectories (`temp/scan_{job_id}_{uuid}/{original_filename}`) rather than mutating the filename string. Always pass an explicit `filename` parameter through all ingestion layers.

