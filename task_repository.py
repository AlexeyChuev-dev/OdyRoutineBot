from datetime import datetime

from database import get_connection
from models import Task


class TaskRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    @staticmethod
    def _row_to_task(row) -> Task:
        return Task(
            id=row["id"],
            user_id=row["user_id"],
            client_id=row["client_id"],
            client_name=row["client_name"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            priority=row["priority"],
            due_at=row["due_at"],
            remind_at=row["remind_at"],
            assignee_user_id=row["assignee_user_id"],
            assignee_name=row["assignee_name"],
            creator_name=row["creator_name"],
        )

    @staticmethod
    def _select_sql() -> str:
        return """
            SELECT
                t.*,
                c.name AS client_name,
                COALESCE(au.first_name, au.username, CAST(t.assignee_user_id AS TEXT)) AS assignee_name,
                COALESCE(cu.first_name, cu.username, CAST(t.user_id AS TEXT)) AS creator_name
            FROM tasks t
            LEFT JOIN clients c ON c.id = t.client_id
            LEFT JOIN users au ON au.id = t.assignee_user_id
            LEFT JOIN users cu ON cu.id = t.user_id
        """

    def create(
        self,
        user_id: int,
        title: str,
        due_at: str | None = None,
        remind_at: str | None = None,
        client_id: int | None = None,
        description: str | None = None,
        priority: str = "normal",
        assignee_user_id: int | None = None,
    ) -> int:
        assignee_user_id = assignee_user_id or user_id

        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            INSERT INTO tasks (
                user_id, assignee_user_id, client_id, title, description,
                priority, due_at, remind_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                assignee_user_id,
                client_id,
                title,
                description,
                priority,
                due_at,
                remind_at,
            ),
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get(self, task_id: int, actor_user_id: int) -> Task | None:
        conn = get_connection(self.database_path)
        row = conn.execute(
            self._select_sql()
            + """
            WHERE t.id = ?
              AND (t.user_id = ? OR t.assignee_user_id = ?)
            """,
            (task_id, actor_user_id, actor_user_id),
        ).fetchone()
        conn.close()
        return self._row_to_task(row) if row else None

    def get_any(self, task_id: int) -> Task | None:
        conn = get_connection(self.database_path)
        row = conn.execute(
            self._select_sql() + " WHERE t.id = ?",
            (task_id,),
        ).fetchone()
        conn.close()
        return self._row_to_task(row) if row else None

    def list_active(self, user_id: int) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.assignee_user_id = ? AND t.status = 'active'
            ORDER BY
                CASE WHEN t.due_at IS NULL THEN 1 ELSE 0 END,
                t.due_at ASC,
                t.id DESC
            """,
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def list_created(self, user_id: int) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.user_id = ?
              AND t.assignee_user_id != t.user_id
              AND t.status = 'active'
            ORDER BY
                CASE WHEN t.due_at IS NULL THEN 1 ELSE 0 END,
                t.due_at ASC,
                t.id DESC
            """,
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def list_for_client(self, user_id: int, client_id: int) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.assignee_user_id = ?
              AND t.client_id = ?
              AND t.status = 'active'
            ORDER BY
                CASE WHEN t.due_at IS NULL THEN 1 ELSE 0 END,
                t.due_at ASC
            """,
            (user_id, client_id),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def list_today(self, user_id: int, day_start: str, day_end: str) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.assignee_user_id = ?
              AND t.status = 'active'
              AND t.due_at >= ?
              AND t.due_at < ?
            ORDER BY t.due_at ASC
            """,
            (user_id, day_start, day_end),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def list_overdue(self, user_id: int, now_iso: str) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.assignee_user_id = ?
              AND t.status = 'active'
              AND t.due_at IS NOT NULL
              AND t.due_at < ?
            ORDER BY t.due_at ASC
            """,
            (user_id, now_iso),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def list_due_reminders(self, now_iso: str) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.status = 'active'
              AND t.remind_at IS NOT NULL
              AND t.reminder_sent = 0
              AND t.remind_at <= ?
            ORDER BY t.remind_at ASC
            """,
            (now_iso,),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def list_active_reminders(self, user_id: int) -> list[Task]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            self._select_sql()
            + """
            WHERE t.assignee_user_id = ?
              AND t.status = 'active'
              AND t.remind_at IS NOT NULL
            ORDER BY t.remind_at ASC
            """,
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_task(row) for row in rows]

    def complete(self, task_id: int, actor_user_id: int) -> bool:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = 'completed', completed_at = ?, updated_at = ?
            WHERE id = ?
              AND status = 'active'
              AND (user_id = ? OR assignee_user_id = ?)
            """,
            (
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
                task_id,
                actor_user_id,
                actor_user_id,
            ),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed

    def delete(self, task_id: int, actor_user_id: int) -> bool:
        # Удалять задачу может только её постановщик.
        # Исполнитель может выполнить или перенести задачу, но не удалить её.
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            DELETE FROM tasks
            WHERE id = ? AND user_id = ?
            """,
            (task_id, actor_user_id),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed

    def move(
        self,
        task_id: int,
        actor_user_id: int,
        due_at: str | None,
        remind_at: str | None = None,
    ) -> bool:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            UPDATE tasks
            SET due_at = ?, remind_at = ?, reminder_sent = 0, updated_at = ?
            WHERE id = ? AND (user_id = ? OR assignee_user_id = ?)
            """,
            (
                due_at,
                remind_at,
                datetime.utcnow().isoformat(),
                task_id,
                actor_user_id,
                actor_user_id,
            ),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed

    def set_reminder(
        self,
        task_id: int,
        actor_user_id: int,
        remind_at: str | None,
    ) -> bool:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            UPDATE tasks
            SET remind_at = ?, reminder_sent = 0, updated_at = ?
            WHERE id = ? AND (user_id = ? OR assignee_user_id = ?)
            """,
            (
                remind_at,
                datetime.utcnow().isoformat(),
                task_id,
                actor_user_id,
                actor_user_id,
            ),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed

    def mark_reminder_sent(self, task_id: int) -> None:
        conn = get_connection(self.database_path)
        conn.execute(
            "UPDATE tasks SET reminder_sent = 1 WHERE id = ?",
            (task_id,),
        )
        conn.commit()
        conn.close()
