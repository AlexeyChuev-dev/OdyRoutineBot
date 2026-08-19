from database import get_connection


class UserRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    def ensure_user(
        self,
        user_id: int,
        username: str | None,
        first_name: str | None,
    ) -> None:
        conn = get_connection(self.database_path)
        conn.execute(
            """
            INSERT INTO users (id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username, first_name),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO settings (user_id)
            VALUES (?)
            """,
            (user_id,),
        )
        conn.commit()
        conn.close()

    def get_settings(self, user_id: int):
        conn = get_connection(self.database_path)
        row = conn.execute(
            """
            SELECT *
            FROM settings
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT OR IGNORE INTO users (id) VALUES (?)",
                (user_id,),
            )
            conn.execute(
                "INSERT OR IGNORE INTO settings (user_id) VALUES (?)",
                (user_id,),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM settings WHERE user_id = ?",
                (user_id,),
            ).fetchone()

        conn.close()
        return dict(row)

    def set_digest(self, user_id: int, kind: str, enabled: bool):
        column = {
            "morning": "morning_digest_enabled",
            "evening": "evening_digest_enabled",
        }[kind]

        conn = get_connection(self.database_path)
        conn.execute(
            f"UPDATE settings SET {column} = ? WHERE user_id = ?",
            (1 if enabled else 0, user_id),
        )
        conn.commit()
        conn.close()

    def list_digest_users(self):
        conn = get_connection(self.database_path)
        rows = conn.execute(
            """
            SELECT u.id, s.*
            FROM users u
            JOIN settings s ON s.user_id = u.id
            WHERE s.morning_digest_enabled = 1
               OR s.evening_digest_enabled = 1
            """
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]
