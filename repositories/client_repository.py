from database import get_connection
from models import Client


class ClientRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    @staticmethod
    def _row_to_client(row) -> Client:
        return Client(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            notes=row["notes"],
        )

    def create(self, user_id: int, name: str, notes: str | None = None) -> int:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            INSERT INTO clients (user_id, name, notes)
            VALUES (?, ?, ?)
            """,
            (user_id, name, notes),
        )
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id

    def list(self, user_id: int) -> list[Client]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            """
            SELECT *
            FROM clients
            WHERE user_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            (user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_client(row) for row in rows]

    def get(self, client_id: int, user_id: int) -> Client | None:
        conn = get_connection(self.database_path)
        row = conn.execute(
            """
            SELECT *
            FROM clients
            WHERE id = ? AND user_id = ?
            """,
            (client_id, user_id),
        ).fetchone()
        conn.close()
        return self._row_to_client(row) if row else None

    def delete(self, client_id: int, user_id: int) -> bool:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            """
            DELETE FROM clients
            WHERE id = ? AND user_id = ?
            """,
            (client_id, user_id),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed
