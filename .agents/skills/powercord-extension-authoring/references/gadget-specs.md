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

