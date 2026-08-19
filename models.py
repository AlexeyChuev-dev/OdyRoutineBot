from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_at: Optional[str]
    remind_at: Optional[str]
    client_id: Optional[int] = None
    client_name: Optional[str] = None
    assignee_user_id: Optional[int] = None
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None


@dataclass
class Client:
    id: int
    user_id: int
    name: str
    notes: Optional[str]


@dataclass
class Person:
    id: int
    owner_user_id: int
    target_user_id: int
    alias: str
    username: Optional[str]
    first_name: Optional[str]


@dataclass
class RecurringTask:
    id: int
    user_id: int
    title: str
    recurrence: str
    weekday: Optional[int]
    day_of_month: Optional[int]
    time: str
    next_run_at: Optional[str]
    is_active: bool
    client_id: Optional[int] = None
    client_name: Optional[str] = None
