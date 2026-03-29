from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta, time
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

    def mark_completed(self) -> Optional[Task]:
        """Mark this task as completed.

        For recurring tasks (daily/weekly), return a new task instance for the next occurrence.
        """
        self.completed = True

        if not self.is_recurring or not self.recurrence_rule:
            return None

        rule = self.recurrence_rule.lower().strip()
        if rule not in ("daily", "weekly"):
            return None

        # derive the base due_time for recurrence; default to today at midnight if absent
        current_due = self.due_time or datetime.combine(date.today(), datetime.min.time())

        if rule == "daily":
            next_due = current_due + timedelta(days=1)
        else:
            next_due = current_due + timedelta(weeks=1)

        next_task = Task(
            id=f"{self.id}-next-{next_due.date().isoformat()}",
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            is_recurring=self.is_recurring,
            recurrence_rule=self.recurrence_rule,
            due_time=next_due,
            category=self.category,
            completed=False,
        )

        return next_task

    def mark_pending(self) -> None:
        """Mark this task as pending/uncompleted."""
        self.completed = False

    def update_duration(self, minutes: int) -> None:
        """Update the task duration, raising on negative values."""
        if minutes < 0:
            raise ValueError("Task duration must be non-negative")
        self.duration_minutes = minutes

    def update_priority(self, priority: int) -> None:
        """Update the task priority with range validation."""
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
        self.priority = priority

    def should_run_today(self, target_date: date) -> bool:
        """Determine whether the task should run on a target date."""
        if self.completed:
            return False
        if self.due_time is not None and self.due_time.date() != target_date:
            return False
        if self.is_recurring:
            return True
        return self.due_time is None or self.due_time.date() == target_date

    def to_dict(self) -> dict:
        """Serialize the task to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "is_recurring": self.is_recurring,
            "recurrence_rule": self.recurrence_rule,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "category": self.category,
            "completed": self.completed,
        }


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
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove task from this pet by ID."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks for this pet."""
        return self.tasks

    def update_profile(self, **kwargs) -> None:
        """Update profile attributes for this pet."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


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
        """Add a pet to the owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name from the owner's list."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def get_pets(self) -> List[Pet]:
        """Return the list of pets owned by this owner."""
        return self.pets

    def get_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name."""
        tasks: List[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                tasks.append(task)
        return tasks

    def update_availability(self, minutes: int) -> None:
        """Update daily available minutes for scheduling."""
        if minutes < 0:
            raise ValueError("Availability minutes must be non-negative")
        self.available_minutes_per_day = minutes


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.schedule_date: Optional[date] = None
        self.scheduled_tasks: List[Task] = []
        self.total_scheduled_minutes: int = 0

    def collect_candidate_tasks(self, target_date: date) -> List[Task]:
        """Collect tasks from all pets that are eligible for the target date.

        This is a lightweight selection algorithm that checks task completion status,
        due date and recurrence to build the candidate pool.
        """
        candidates: List[Task] = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.should_run_today(target_date):
                    candidates.append(task)
        return candidates

    def sort_tasks_by_priority_due(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority first, due date second, and duration third.

        This method provides a deterministic ordering for greedy schedule fitting.
        """
        return sorted(
            tasks,
            key=lambda task: (
                -task.priority,
                task.due_time or datetime.max,
                task.duration_minutes,
            ),
        )

    def fit_tasks_by_availability(self, tasks: List[Task]) -> List[Task]:
        """Greedily fit tasks into owner availability, preserving order.

        The algorithm is O(n), selecting tasks in provided order and truncating at
        availability limits. This is a simple and transparent strategy for users,
        but it does not guarantee an optimal total priority solution.
        """
        available = self.owner.available_minutes_per_day
        schedule: List[Task] = []

        for task in tasks:
            if task.duration_minutes <= 0:
                continue
            if task.duration_minutes <= available:
                schedule.append(task)
                available -= task.duration_minutes

        self.total_scheduled_minutes = self.owner.available_minutes_per_day - available
        return schedule

    def generate_daily_plan(self, target_date: date) -> None:
        """Generate a daily task plan for the target date."""
        self.schedule_date = target_date
        candidate_tasks = self.collect_candidate_tasks(target_date)
        ordered_tasks = self.sort_tasks_by_priority_due(candidate_tasks)
        self.scheduled_tasks = self.fit_tasks_by_availability(ordered_tasks)

    def get_schedule(self) -> List[Task]:
        """Return the generated schedule tasks."""
        return self.scheduled_tasks

    def explain_plan(self) -> str:
        """Provide a human-readable explanation of the generated plan."""
        if not self.schedule_date:
            return "No schedule generated yet."

        lines = [f"Schedule for {self.schedule_date.isoformat()}:" ]
        for task in self.scheduled_tasks:
            lines.append(
                f"- {task.title} ({task.duration_minutes} minutes, priority {task.priority})"
            )

        slack = self.owner.available_minutes_per_day - self.total_scheduled_minutes
        lines.append(f"Total scheduled minutes: {self.total_scheduled_minutes}")
        lines.append(f"Remaining available minutes: {slack}")

        conflicts = self.detect_conflicts(self.scheduled_tasks)
        if conflicts:
            lines.append("Conflicts:")
            lines.extend([f"- {c}" for c in conflicts])

        return "\n".join(lines)

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Detect conflicts in the current schedule and return descriptions.

        Conflict checks are non-fatal warnings.  This method performs an efficient
        evaluation over:

        - total availability budget
        - duplicate task IDs
        - task duration bounds
        - timed task overlaps (same or overlapping minutes)

        The result is a list of warning strings and the scheduler continues to use
        the plan regardless.
        """
        conflicts: List[str] = []
        if self.total_scheduled_minutes > self.owner.available_minutes_per_day:
            conflicts.append("WARNING: Scheduled workload exceeds available minutes.")

        task_ids = [task.id for task in tasks]
        if len(task_ids) != len(set(task_ids)):
            conflicts.append("WARNING: Duplicate task IDs in schedule.")

        too_long = [task for task in tasks if task.duration_minutes > self.owner.available_minutes_per_day]
        for task in too_long:
            conflicts.append(
                f"WARNING: Task '{task.title}' duration ({task.duration_minutes}) exceeds total daily availability ({self.owner.available_minutes_per_day})."
            )

        # Detect overlapping scheduled-task time windows for tasks with defined due_time.
        timed_tasks = [
            task
            for task in tasks
            if task.due_time is not None and task.duration_minutes > 0
        ]

        timed_tasks.sort(key=lambda t: t.due_time)

        for i in range(len(timed_tasks)):
            current_task = timed_tasks[i]
            current_start = current_task.due_time
            current_end = current_start + timedelta(minutes=current_task.duration_minutes)

            for j in range(i + 1, len(timed_tasks)):
                next_task = timed_tasks[j]
                next_start = next_task.due_time
                next_end = next_start + timedelta(minutes=next_task.duration_minutes)

                if next_start >= current_end:
                    break

                # Overlap found between current_task and next_task
                conflicts.append(
                    f"WARNING: Task '{current_task.title}' ({current_start.time()}-{current_end.time()})" \
                    f" overlaps with '{next_task.title}' ({next_start.time()}-{next_end.time()})."
                )

        return conflicts

