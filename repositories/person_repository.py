import re
import sqlite3

from database import get_connection
from models import Person


def _normalize(value: str) -> str:
    return re.sub(
        r"[^a-zа-яё0-9_-]",
        "",
        value.lower().replace("ё", "е").lstrip("@"),
    )


class PersonRepository:
    def __init__(self, database_path: str):
        self.database_path = database_path

    @staticmethod
    def _row_to_person(row) -> Person:
        return Person(
            id=row["id"],
            owner_user_id=row["owner_user_id"],
            target_user_id=row["target_user_id"],
            alias=row["alias"],
            username=row["username"],
            first_name=row["first_name"],
        )

    def list(self, owner_user_id: int) -> list[Person]:
        conn = get_connection(self.database_path)
        rows = conn.execute(
            """
            SELECT p.*, u.username, u.first_name
            FROM task_people p
            JOIN users u ON u.id = p.target_user_id
            WHERE p.owner_user_id = ?
            ORDER BY p.alias COLLATE NOCASE
            """,
            (owner_user_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_person(row) for row in rows]

    def get(self, person_id: int, owner_user_id: int) -> Person | None:
        conn = get_connection(self.database_path)
        row = conn.execute(
            """
            SELECT p.*, u.username, u.first_name
            FROM task_people p
            JOIN users u ON u.id = p.target_user_id
            WHERE p.id = ? AND p.owner_user_id = ?
            """,
            (person_id, owner_user_id),
        ).fetchone()
        conn.close()
        return self._row_to_person(row) if row else None

    def create(
        self,
        owner_user_id: int,
        target_user_id: int,
        alias: str,
    ) -> tuple[int | None, str | None]:
        conn = get_connection(self.database_path)
        try:
            cursor = conn.execute(
                """
                INSERT INTO task_people (owner_user_id, target_user_id, alias)
                VALUES (?, ?, ?)
                """,
                (owner_user_id, target_user_id, alias.strip()),
            )
            conn.commit()
            return cursor.lastrowid, None
        except sqlite3.IntegrityError:
            return None, "Такой человек или алиас уже добавлен."
        finally:
            conn.close()

    def delete(self, person_id: int, owner_user_id: int) -> bool:
        conn = get_connection(self.database_path)
        cursor = conn.execute(
            "DELETE FROM task_people WHERE id = ? AND owner_user_id = ?",
            (person_id, owner_user_id),
        )
        conn.commit()
        changed = cursor.rowcount > 0
        conn.close()
        return changed

    def resolve(self, owner_user_id: int, token: str) -> Person | None:
        normalized = _normalize(token)
        if not normalized:
            return None

        people = self.list(owner_user_id)

        # Сначала точное совпадение по алиасу / username / имени.
        for person in people:
            candidates = {
                _normalize(person.alias),
                _normalize(person.username or ""),
                _normalize(person.first_name or ""),
            }
            candidates.discard("")
            if normalized in candidates:
                return person

        # Затем мягкое совпадение для русских падежей:
        # "Артем" -> "Артему", "Дима" -> "Диме" и т.п.
        for person in people:
            candidates = [
                _normalize(person.alias),
                _normalize(person.first_name or ""),
            ]
            for candidate in candidates:
                if len(candidate) < 3:
                    continue
                common = 0
                for left, right in zip(normalized, candidate):
                    if left != right:
                        break
                    common += 1
                if common >= min(4, len(candidate)):
                    return person

        return None
