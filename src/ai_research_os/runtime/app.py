from __future__ import annotations

from pathlib import Path

from ai_research_os.config.settings import get_settings
from ai_research_os.storage.sqlite import connect_sqlite, initialize_database


def load_schema() -> str:
    root = Path(__file__).resolve().parents[3]
    schema_path = root / "migrations" / "0001_init.sql"
    return schema_path.read_text(encoding="utf-8")


def main() -> None:
    settings = get_settings()
    conn = connect_sqlite(settings.sqlite_db_path)
    initialize_database(conn, load_schema())
    print(f"ai-research-os initialized at {settings.sqlite_db_path}")
    print("phase1 profile: sqlite-first, discord-first, durable-queue-ready")


if __name__ == "__main__":
    main()
