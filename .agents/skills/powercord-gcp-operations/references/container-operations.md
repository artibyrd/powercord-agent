# Production Container Operations Reference

---

## 1. Golden Rule of Production Execution

Production Container-Optimized OS does not have `poetry` or `just`. Always invoke Python directly via the virtualenv binary:
```bash
/app/.venv/bin/python
```

---

## 2. Remote Command Examples

* **Add API Key**:
  ```bash
  docker exec <CONTAINER_ID> /app/.venv/bin/python app/db/manage_api_keys.py add "LuteBot Legacy Key" --scopes '["midi_library"]' --key "your-key"
  ```
* **Rescore MIDI Library**:
  ```bash
  docker exec -e POWERCORD_DB_HOST=localhost:5432 <CONTAINER_ID> /app/.venv/bin/python -m app.extensions.midi_library.rescore
  ```
* **Database Restore**:
  ```bash
  docker exec -it <CONTAINER_ID> /app/.venv/bin/python app/db/db_tools.py import /app/your_dump_file.sql
  ```
