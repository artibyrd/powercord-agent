#!/usr/bin/env python3
"""Pure-stdlib integrity linter for the powercord-agent native plugin repository.

Validates:
1. plugin.json manifest schema, SemVer, allowed keys, logo asset, and <=3 suggestedPrompts.
2. skills/*/SKILL.md YAML frontmatter, size limits, and relative Markdown links.
3. rules/AGENTS.md presence, <800-token context budget, and Living Canon slug discipline.
4. overrides/*.md 3-section delta schema (Overrides, Extensions, Disabled / Not Applicable).
5. hooks.json structure and existence of referenced hook scripts.
6. mcp_config.json JSON validity.
7. Zero hardcoded machine-local user paths across tracked repository files.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]

ALLOWED_PLUGIN_FIELDS = {
    "name",
    "displayName",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "logo",
    "suggestedPrompts",
    "disabled",
}
REQUIRED_PLUGIN_FIELDS = {
    "name",
    "displayName",
    "version",
    "description",
    "author",
    "repository",
    "logo",
    "suggestedPrompts",
}
VALID_LOGO_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg", ".webp"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_OVERLAY_SECTIONS = (
    "## Overrides",
    "## Extensions",
    "## Disabled / Not Applicable",
)
EXPECTED_OVERLAYS = {
    "architecture-review.md",
    "bootstrap-approvals.md",
    "domain-modeling.md",
    "knowledge-governance.md",
    "pr-brief.md",
    "release-lifecycle.md",
}

MAX_SKILL_LINES = 500
MAX_SKILL_BYTES = 20_000
MAX_AGENTS_TOKENS = 800

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Constructed via concatenation so naive literal substring scans never false-positive on the detector itself.
LOCAL_PATH_RE = re.compile(
    r"(?:/"
    r"home/[A-Za-z0-9._-]+/|/"
    r"Users/[A-Za-z0-9._-]+/|[A-Za-z]:\\"
    r"Users\\[A-Za-z0-9._-]+\\)"
)
LIVING_CANON_RE = re.compile(
    r"\b(\d+)\s+(system\s+invariants|core\s+invariants|universal\s+invariants)\b",
    re.IGNORECASE,
)


def _strip_fenced_code(text: str) -> str:
    """Remove fenced code blocks before scanning for Markdown links."""
    out_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out_lines.append(line)
    return "\n".join(out_lines)


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal pure-stdlib parser for simple YAML frontmatter (name + description)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None

    fm: dict[str, str] = {}
    current_key: str | None = None
    block_lines: list[str] = []

    def _flush() -> None:
        nonlocal current_key, block_lines
        if current_key is not None:
            fm[current_key] = " ".join(s.strip() for s in block_lines if s.strip()).strip()
        current_key = None
        block_lines = []

    for raw in lines[1:end_idx]:
        if raw.startswith((" ", "\t")) and current_key is not None:
            block_lines.append(raw)
            continue
        if ":" in raw:
            _flush()
            key, val = raw.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val in (">", ">-", "|", "|-"):
                current_key = key
                block_lines = []
            else:
                fm[key] = val.strip("\"'")
    _flush()
    return fm


def check_plugin_json(errors: list[str]) -> None:
    path = PLUGIN_ROOT / "plugin.json"
    if not path.exists():
        errors.append("Missing plugin.json at plugin root.")
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"plugin.json invalid JSON: {exc}")
        return

    if not isinstance(data, dict):
        errors.append("plugin.json root must be a JSON object.")
        return

    unknown = set(data.keys()) - ALLOWED_PLUGIN_FIELDS
    if unknown:
        errors.append(f"plugin.json contains unsupported top-level fields: {sorted(unknown)}")

    missing = REQUIRED_PLUGIN_FIELDS - set(data.keys())
    if missing:
        errors.append(f"plugin.json missing required fields: {sorted(missing)}")

    name = data.get("name", "")
    if not isinstance(name, str) or not KEBAB_RE.match(name):
        errors.append(f"plugin.json 'name' must be lowercase kebab-case, got: {name!r}")

    version = data.get("version", "")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        errors.append(f"plugin.json 'version' must be valid SemVer, got: {version!r}")

    logo = data.get("logo", "")
    if not isinstance(logo, str) or logo.startswith(("/", "http://", "https://")):
        errors.append(f"plugin.json 'logo' must be a relative path, got: {logo!r}")
    else:
        logo_path = PLUGIN_ROOT / logo
        if not logo_path.is_file():
            errors.append(f"plugin.json 'logo' target does not exist: {logo}")
        elif logo_path.suffix.lower() not in VALID_LOGO_SUFFIXES:
            errors.append(f"plugin.json 'logo' unsupported extension: {logo_path.suffix}")

    prompts = data.get("suggestedPrompts")
    if not isinstance(prompts, list) or not (1 <= len(prompts) <= 3):
        errors.append("plugin.json 'suggestedPrompts' must be a list of 1 to 3 strings.")
    elif any(not isinstance(p, str) or not p.strip() for p in prompts):
        errors.append("plugin.json 'suggestedPrompts' must contain non-empty strings.")


def check_skills(errors: list[str]) -> None:
    skills_dir = PLUGIN_ROOT / "skills"
    if not skills_dir.is_dir():
        errors.append("Missing skills/ directory at plugin root.")
        return

    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        errors.append("No skills found under skills/.")
        return

    for sdir in skill_dirs:
        skill_md = sdir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"skills/{sdir.name}: missing SKILL.md")
            continue

        raw = skill_md.read_text(encoding="utf-8")
        lines = raw.splitlines()
        size_bytes = len(raw.encode("utf-8"))
        if len(lines) > MAX_SKILL_LINES:
            errors.append(f"skills/{sdir.name}/SKILL.md exceeds {MAX_SKILL_LINES} lines ({len(lines)}).")
        if size_bytes > MAX_SKILL_BYTES:
            errors.append(f"skills/{sdir.name}/SKILL.md exceeds {MAX_SKILL_BYTES} bytes ({size_bytes}).")

        fm = _parse_frontmatter(raw)
        if fm is None:
            errors.append(f"skills/{sdir.name}/SKILL.md missing valid YAML frontmatter.")
        else:
            if fm.get("name") != sdir.name:
                errors.append(
                    f"skills/{sdir.name}/SKILL.md frontmatter name {fm.get('name')!r} != dir name {sdir.name!r}"
                )
            if not fm.get("description"):
                errors.append(f"skills/{sdir.name}/SKILL.md missing non-empty 'description' in frontmatter.")
            extra_keys = set(fm.keys()) - {"name", "description"}
            if extra_keys:
                errors.append(
                    f"skills/{sdir.name}/SKILL.md frontmatter must only declare name/description, got {sorted(extra_keys)}"
                )

        # Validate relative links across SKILL.md and references/*.md
        for md_file in sorted(sdir.rglob("*.md")):
            body = _strip_fenced_code(md_file.read_text(encoding="utf-8"))
            for match in MD_LINK_RE.finditer(body):
                target = match.group(1).strip()
                if not target or target.startswith(("http://", "https://", "mailto:", "#", "customization://")):
                    continue
                target_path = target.split("#", 1)[0]
                if not target_path:
                    continue
                resolved = (md_file.parent / target_path).resolve()
                if not resolved.exists():
                    rel = md_file.relative_to(PLUGIN_ROOT)
                    errors.append(f"Broken relative link in {rel}: ({target})")


def check_rules_agents_md(errors: list[str]) -> None:
    rules_md = PLUGIN_ROOT / "rules" / "AGENTS.md"
    if not rules_md.is_file():
        errors.append("Missing rules/AGENTS.md at native plugin path.")
        return

    text = rules_md.read_text(encoding="utf-8")
    words = text.split()
    est_tokens = int(len(words) * 1.33)
    if est_tokens > MAX_AGENTS_TOKENS:
        errors.append(
            f"rules/AGENTS.md exceeds {MAX_AGENTS_TOKENS}-token budget: {est_tokens} est. tokens ({len(words)} words)."
        )

    if LIVING_CANON_RE.search(text):
        errors.append("rules/AGENTS.md violates Living Canon (hardcoded invariant count detected).")


def check_overrides(errors: list[str]) -> None:
    ov_dir = PLUGIN_ROOT / "overrides"
    if not ov_dir.is_dir():
        errors.append("Missing overrides/ directory.")
        return

    found = {p.name for p in ov_dir.glob("*.md")}
    missing = EXPECTED_OVERLAYS - found
    if missing:
        errors.append(f"Missing expected overlays in overrides/: {sorted(missing)}")

    for ov_file in sorted(ov_dir.glob("*.md")):
        if ov_file.name == "SKILL.md":
            errors.append("overrides/ must never contain SKILL.md (must remain 0 always-on tokens).")
            continue
        text = ov_file.read_text(encoding="utf-8")
        positions: list[int] = []
        for heading in REQUIRED_OVERLAY_SECTIONS:
            pattern = re.compile(rf"^{re.escape(heading)}\s*$", re.MULTILINE)
            match = pattern.search(text)
            if not match:
                errors.append(f"overrides/{ov_file.name}: missing required section '{heading}'")
            else:
                positions.append(match.start())
        if len(positions) == len(REQUIRED_OVERLAY_SECTIONS) and positions != sorted(positions):
            errors.append(
                f"overrides/{ov_file.name}: sections must appear in order {list(REQUIRED_OVERLAY_SECTIONS)}"
            )
        if LIVING_CANON_RE.search(text):
            errors.append(
                f"overrides/{ov_file.name}: violates Living Canon (hardcoded invariant count detected)."
            )


def check_hooks_and_mcp(errors: list[str]) -> None:
    hooks_json = PLUGIN_ROOT / "hooks.json"
    if not hooks_json.is_file():
        errors.append("Missing hooks.json at plugin root.")
    else:
        try:
            hooks_data = json.loads(hooks_json.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"hooks.json invalid JSON: {exc}")
            hooks_data = None

        if isinstance(hooks_data, dict):
            for hook_name, spec in hooks_data.items():
                if not isinstance(spec, dict):
                    errors.append(f"hooks.json[{hook_name!r}] must be an object.")
                    continue
                for event_name, entries in spec.items():
                    if event_name == "enabled" or not isinstance(entries, list):
                        continue
                    for entry in entries:
                        handlers = entry.get("hooks", [entry]) if isinstance(entry, dict) else []
                        for handler in handlers:
                            cmd = handler.get("command", "") if isinstance(handler, dict) else ""
                            if not cmd:
                                errors.append(f"hooks.json[{hook_name!r}].{event_name} handler missing 'command'.")
                                continue
                            tokens = shlex.split(cmd)
                            script_tokens = [
                                t for t in tokens if t.startswith("./") or t.endswith((".py", ".sh"))
                            ]
                            if not script_tokens:
                                errors.append(
                                    f"hooks.json[{hook_name!r}] command does not reference a local script: {cmd!r}"
                                )
                            for script_ref in script_tokens:
                                target = (PLUGIN_ROOT / script_ref).resolve()
                                if not target.is_file():
                                    errors.append(
                                        f"hooks.json[{hook_name!r}] script target missing: {script_ref}"
                                    )

    mcp_json = PLUGIN_ROOT / "mcp_config.json"
    if not mcp_json.is_file():
        errors.append("Missing mcp_config.json at plugin root.")
    else:
        try:
            mcp_data = json.loads(mcp_json.read_text(encoding="utf-8"))
            if not isinstance(mcp_data, dict) or not isinstance(mcp_data.get("mcpServers"), dict):
                errors.append("mcp_config.json must define a 'mcpServers' object.")
        except Exception as exc:
            errors.append(f"mcp_config.json invalid JSON: {exc}")


def check_no_local_paths_or_legacy_dirs(errors: list[str]) -> None:
    if (PLUGIN_ROOT / ".agents").exists():
        errors.append("Legacy .agents/ directory must not exist inside native powercord-agent plugin.")

    if (PLUGIN_ROOT / "AGENTS.md").exists():
        errors.append("Root powercord-agent/AGENTS.md must be moved to rules/AGENTS.md.")

    skip_dirs = {".git", "__pycache__", ".venv", "node_modules"}
    text_suffixes = {".md", ".json", ".py", ".sh", ".yml", ".yaml", ".toml", ".txt", ".svg"}

    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in text_suffixes and path.name != ".gitignore":
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(PLUGIN_ROOT)
        for lineno, line in enumerate(content.splitlines(), start=1):
            if LOCAL_PATH_RE.search(line):
                errors.append(f"Machine-local path detected in {rel}:{lineno}: {line.strip()}")


def main() -> int:
    errors: list[str] = []
    check_plugin_json(errors)
    check_skills(errors)
    check_rules_agents_md(errors)
    check_overrides(errors)
    check_hooks_and_mcp(errors)
    check_no_local_paths_or_legacy_dirs(errors)

    if errors:
        print("powercord-agent lint FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    skill_count = sum(
        1 for p in (PLUGIN_ROOT / "skills").iterdir() if p.is_dir() and not p.name.startswith(".")
    )
    overlay_count = len(list((PLUGIN_ROOT / "overrides").glob("*.md")))
    words = (PLUGIN_ROOT / "rules" / "AGENTS.md").read_text(encoding="utf-8").split()
    print(
        f"powercord-agent lint PASSED "
        f"({skill_count} skills, {overlay_count} overlays, "
        f"rules/AGENTS.md={int(len(words) * 1.33)} est. tokens)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
