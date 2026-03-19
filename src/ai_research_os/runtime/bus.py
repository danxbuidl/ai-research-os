from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


class SQLiteOutbox:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def publish(
        self,
        *,
        topic: str,
        payload: dict[str, Any],
        correlation_id: str = "",
        proposal_id: str = "",
        trace_id: str = "",
        producer_agent: str = "",
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT INTO outbox_events("
            "topic, payload_json, correlation_id, proposal_id, trace_id, producer_agent, "
            "status, attempt_count, available_at, created_at, updated_at"
            ") VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?, ?, ?)",
            (
                topic,
                json.dumps(payload, ensure_ascii=False),
                correlation_id,
                proposal_id,
                trace_id,
                producer_agent,
                now,
                now,
                now,
            ),
        )
        self._conn.commit()

    def claim_pending(self, topic: str, limit: int = 20) -> list[sqlite3.Row]:
        rows = self._conn.execute(
            "SELECT * FROM outbox_events WHERE topic = ? AND status = 'pending' "
            "AND available_at <= ? ORDER BY id ASC LIMIT ?",
            (topic, datetime.now(timezone.utc).isoformat(), limit),
        ).fetchall()
        if not rows:
            return []
        now = datetime.now(timezone.utc).isoformat()
        for row in rows:
            self._conn.execute(
                "UPDATE outbox_events SET status = 'running', attempt_count = attempt_count + 1, "
                "updated_at = ? WHERE id = ?",
                (now, row["id"]),
            )
        self._conn.commit()
        return rows

    def mark_done(self, event_id: int) -> None:
        self._conn.execute(
            "UPDATE outbox_events SET status = 'done', updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), event_id),
        )
        self._conn.commit()

    def mark_failed(self, event_id: int, error: str) -> None:
        self._conn.execute(
            "UPDATE outbox_events SET status = 'failed', last_error = ?, updated_at = ? WHERE id = ?",
            (error[:500], datetime.now(timezone.utc).isoformat(), event_id),
        )
        self._conn.commit()


class SQLiteTaskQueue:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def enqueue(
        self,
        *,
        task_id: str,
        task_type: str,
        proposal_id: str,
        trace_id: str,
        assigned_agent: str,
        payload: dict[str, Any],
        checkpoint_state: str = "NEW",
        status: str = "pending",
        resume_token: str = "",
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR REPLACE INTO agent_tasks("
            "task_id, task_type, proposal_id, trace_id, assigned_agent, payload_json, "
            "checkpoint_state, status, attempt_count, resume_token, available_at, "
            "created_at, updated_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)",
            (
                task_id,
                task_type,
                proposal_id,
                trace_id,
                assigned_agent,
                json.dumps(payload, ensure_ascii=False),
                checkpoint_state,
                status,
                resume_token,
                now,
                now,
                now,
            ),
        )
        self._conn.commit()

    def claim_pending(self, assigned_agent: str, limit: int = 20) -> list[sqlite3.Row]:
        now = datetime.now(timezone.utc).isoformat()
        rows = self._conn.execute(
            "SELECT * FROM agent_tasks WHERE assigned_agent = ? AND status = 'pending' "
            "AND available_at <= ? ORDER BY created_at ASC LIMIT ?",
            (assigned_agent, now, limit),
        ).fetchall()
        for row in rows:
            self._conn.execute(
                "UPDATE agent_tasks SET status = 'running', attempt_count = attempt_count + 1, "
                "updated_at = ? WHERE task_id = ?",
                (now, row["task_id"]),
            )
        if rows:
            self._conn.commit()
        return rows

    def mark_waiting_human(self, task_id: str, *, checkpoint_state: str, resume_token: str) -> None:
        self._conn.execute(
            "UPDATE agent_tasks SET status = 'waiting_human', checkpoint_state = ?, "
            "resume_token = ?, updated_at = ? WHERE task_id = ?",
            (
                checkpoint_state,
                resume_token,
                datetime.now(timezone.utc).isoformat(),
                task_id,
            ),
        )
        self._conn.commit()

    def resume_by_token(self, resume_token: str) -> sqlite3.Row | None:
        row = self._conn.execute(
            "SELECT * FROM agent_tasks WHERE resume_token = ? AND status = 'waiting_human' LIMIT 1",
            (resume_token,),
        ).fetchone()
        if row is None:
            return None
        self._conn.execute(
            "UPDATE agent_tasks SET status = 'pending', updated_at = ? WHERE task_id = ?",
            (datetime.now(timezone.utc).isoformat(), row["task_id"]),
        )
        self._conn.commit()
        return row

    def mark_done(self, task_id: str) -> None:
        self._conn.execute(
            "UPDATE agent_tasks SET status = 'done', updated_at = ? WHERE task_id = ?",
            (datetime.now(timezone.utc).isoformat(), task_id),
        )
        self._conn.commit()

    def mark_failed(self, task_id: str, error: str) -> None:
        self._conn.execute(
            "UPDATE agent_tasks SET status = 'failed', last_error = ?, updated_at = ? WHERE task_id = ?",
            (error[:500], datetime.now(timezone.utc).isoformat(), task_id),
        )
        self._conn.commit()
