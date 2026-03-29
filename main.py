from datetime import datetime, date

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # Create owner with daily availability (e.g., 120 minutes per day)
    owner = Owner(name="Alex", email="alex@example.com", timezone="US/Pacific", available_minutes_per_day=120)

    # Create two pets with tasks
    dog = Pet(name="Fido", species="Dog", breed="Labrador", age=4)
    cat = Pet(name="Whiskers", species="Cat", breed="Siamese", age=3)

    owner.add_pet(dog)
    owner.add_pet(cat)

    # Add tasks (different duration and priorities)
    task1 = Task(
        id="t1",
        title="Morning walk",
        description="30-min walk in the park",
        duration_minutes=30,
        priority=5,
        is_recurring=True,
        recurrence_rule="daily",
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=7, minute=0),
        category="Exercise",
    )

    task2 = Task(
        id="t2",
        title="Medication",
        description="Give pill after breakfast",
        duration_minutes=10,
        priority=5,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=8, minute=0),
        category="Health",
    )

    task3 = Task(
        id="t3",
        title="Grooming",
        description="Brush for 20 minutes",
        duration_minutes=20,
        priority=3,
        category="Grooming",
    )

    dog.add_task(task1)
    dog.add_task(task2)
    cat.add_task(task3)

    # Mark recurring task completed and auto-create next occurrence
    next_task = task1.mark_completed()
    if next_task:
        dog.add_task(next_task)

    # Add more tasks out of order deliberately
    task4 = Task(
        id="t4",
        title="Evening play",
        description="15-min fetch/play session",
        duration_minutes=15,
        priority=4,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=19, minute=0),
        category="Play",
    )
    task5 = Task(
        id="t5",
        title="Lunch snack",
        description="Give cat lunch snack",
        duration_minutes=5,
        priority=2,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=12, minute=30),
        category="Food",
    )

    # Add overlapping same-time tasks to trigger conflict warning
    task_overlap1 = Task(
        id="t6",
        title="Vet check",
        description="Quick vet check",
        duration_minutes=30,
        priority=5,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=10, minute=0),
        category="Health",
    )
    task_overlap2 = Task(
        id="t7",
        title="Grooming quick",
        description="Quick grooming overlap",
        duration_minutes=30,
        priority=4,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=10, minute=0),
        category="Grooming",
    )

    dog.add_task(task4)
    cat.add_task(task5)
    dog.add_task(task_overlap1)
    cat.add_task(task_overlap2)

    # Mark one task completed for filtering test
    task2.mark_completed()

    # Configure and run scheduler
    scheduler = Scheduler(owner=owner)
    scheduler.generate_daily_plan(date.today())

    # Print schedule
    print("Today's Schedule")
    print("====================")
    print(scheduler.explain_plan())

    # Use Owner filter API
    print("\nFiltered tasks (pending):")
    pending_tasks = owner.get_tasks(completed=False)
    for t in pending_tasks:
        print(f"- {t.id} {t.title} ({t.duration_minutes}m) for {t.category}")

    print("\nFiltered tasks (Fido all):")
    fido_tasks = owner.get_tasks(pet_name="Fido")
    for t in fido_tasks:
        print(f"- {t.id} {t.title} completed={t.completed} due={t.due_time}")

    # Sort by due_time explicitly (HH:MM chronological order)
    def hhmm_key(task: Task):
        if not task.due_time:
            return datetime.max.time()
        return task.due_time.time()

    sorted_by_time = sorted(pending_tasks, key=hhmm_key)
    print("\nPending tasks sorted by due_time:")
    for t in sorted_by_time:
        print(f"- {t.title} at {t.due_time.time() if t.due_time else 'N/A'}")


if __name__ == "__main__":
    main()