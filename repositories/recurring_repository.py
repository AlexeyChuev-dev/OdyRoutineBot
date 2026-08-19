from database import get_connection
from models import RecurringTask


class RecurringRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    @staticmethod
    def _row_to_item(row) -> RecurringTask:
        return RecurringTask(
            id=row["id"],
            user_id=row["user_id"],
            client_id=row["client_id"],
            client_name=row["client_name"],
            title=row["title"],
            recurrence=row["recurrence"],
            weekday=row["weekday"],
            day_of_month=row["day_of_month"],
            time=row["time"],
            next_run_at=row["next_run_at"],
            is_active=bool(row["is_active"]),
        )

    def create(
        self,
        user_id: int,
        title: str,
        recurrence: str,
        time: str,
        next_run_at: str,
        weekday: int | None = None,
        client_id: int | None = None,
    ) -> int:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            INSERT INTO recurring_tasks (
                user_id, client_id, title, recurrence,
                weekday, time, next_run_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                client_id,
                title,
                recurrence,
                weekday,
                time,
                next_run_at,
            ),
        )
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id

    def list(self, user_id: int) -> list[RecurringTask]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            """
            SELECT r.*, c.name AS client_name
            FROM recurring_tasks r
            LEFT JOIN clients c ON c.id = r.client_id
            WHERE r.user_id = ?
            ORDER BY r.is_active DESC, r.next_run_at ASC
            """,
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def list_due(self, now_iso: str) -> list[RecurringTask]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            """
            SELECT r.*, c.name AS client_name
            FROM recurring_tasks r
            LEFT JOIN clients c ON c.id = r.client_id
            WHERE r.is_active = 1
              AND r.next_run_at IS NOT NULL
              AND r.next_run_at <= ?
            ORDER BY r.next_run_at ASC
            """,
            (now_iso,),
        ).fetchall()
        conn.close()
        return [self._row_to_item(row) for row in rows]

    def update_next_run(self, item_id: int, next_run_at: str) -> None:
        conn = get_connection(self.database_path)
        conn.execute(
            """
            UPDATE recurring_tasks
            SET next_run_at = ?
            WHERE id = ?
            """,
            (next_run_at, item_id),
        )
        conn.commit()
        conn.close()
