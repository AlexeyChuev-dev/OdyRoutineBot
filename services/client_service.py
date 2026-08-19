import sqlite3

from repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def create(self, user_id: int, name: str, notes: str | None = None):
        name = name.strip()
        if not name:
            return None, "Название клиента не может быть пустым."

        try:
            client_id = self.repository.create(user_id, name, notes)
        except sqlite3.IntegrityError:
            return None, "Такой клиент уже существует."

        return client_id, None
