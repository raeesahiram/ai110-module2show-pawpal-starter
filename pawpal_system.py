from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional


@dataclass
class Task:
    id: str
    title: str
    description: Optional[str] = None
    duration_minutes: int = 0
    priority: int = 3  # 1 (low) .. 5 (high)
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    due_time: Optional[datetime] = None
    category: Optional[str] = None
    completed: bool = False

    def mark_completed(self) -> None:
        raise NotImplementedError

    def mark_pending(self) -> None:
        raise NotImplementedError

    def update_duration(self, minutes: int) -> None:
        raise NotImplementedError

    def update_priority(self, priority: int) -> None:
        raise NotImplementedError

    def should_run_today(self, target_date: date) -> bool:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    size: Optional[str] = None
    special_needs: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_tasks(self) -> List[Task]:
        raise NotImplementedError

    def update_profile(self, **kwargs) -> None:
        raise NotImplementedError


class Owner:
    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        timezone: Optional[str] = None,
        available_minutes_per_day: int = 0,
    ):
        self.name = name
        self.email = email
        self.timezone = timezone
        self.available_minutes_per_day = available_minutes_per_day
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet_name: str) -> None:
        raise NotImplementedError

    def get_pets(self) -> List[Pet]:
        raise NotImplementedError

    def update_availability(self, minutes: int) -> None:
        raise NotImplementedError


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule_date: Optional[date] = None
        self.scheduled_tasks: List[Task] = []
        self.total_scheduled_minutes: int = 0

    def collect_candidate_tasks(self, target_date: date) -> List[Task]:
        raise NotImplementedError

    def sort_tasks_by_priority_due(self, tasks: List[Task]) -> List[Task]:
        raise NotImplementedError

    def fit_tasks_by_availability(self, tasks: List[Task]) -> List[Task]:
        raise NotImplementedError

    def generate_daily_plan(self, target_date: date) -> None:
        raise NotImplementedError

    def get_schedule(self) -> List[Task]:
        raise NotImplementedError

    def explain_plan(self) -> str:
        raise NotImplementedError

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        raise NotImplementedError
