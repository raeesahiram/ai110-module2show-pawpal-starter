from datetime import datetime, date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion_sets_completed_true():
    task = Task(
        id="test-1",
        title="Test task",
        duration_minutes=10,
        priority=3,
    )

    task.mark_completed()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    initial_count = len(pet.get_tasks())

    task = Task(
        id="test-2",
        title="Feed",
        duration_minutes=5,
        priority=4,
    )

    pet.add_task(task)

    assert len(pet.get_tasks()) == initial_count + 1


def test_scheduler_detects_overlapping_tasks():
    owner = Owner(name="Alex", available_minutes_per_day=120)
    pet = Pet(name="Fido", species="Dog")
    owner.add_pet(pet)

    task_a = Task(
        id="overlap-1",
        title="Breakfast",
        duration_minutes=30,
        priority=4,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=8, minute=0),
    )
    task_b = Task(
        id="overlap-2",
        title="Morning walk",
        duration_minutes=45,
        priority=4,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=8, minute=15),
    )

    pet.add_task(task_a)
    pet.add_task(task_b)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_daily_plan(date.today())

    conflicts = scheduler.detect_conflicts(scheduler.scheduled_tasks)
    assert any("overlaps" in c for c in conflicts)
    assert any(c.startswith("WARNING:") for c in conflicts)


def test_sort_tasks_by_priority_due_chronological_order():
    owner = Owner(name="Alex", available_minutes_per_day=180)
    pet = Pet(name="Fido", species="Dog")
    owner.add_pet(pet)

    task_a = Task(
        id="s1",
        title="Morning feed",
        duration_minutes=10,
        priority=3,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=9, minute=0),
    )
    task_b = Task(
        id="s2",
        title="Vet drop-in",
        duration_minutes=30,
        priority=3,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=10, minute=0),
    )
    task_c = Task(
        id="s3",
        title="Afternoon play",
        duration_minutes=20,
        priority=3,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=11, minute=0),
    )

    tasks = [task_b, task_c, task_a]
    scheduler = Scheduler(owner=owner)
    ordered = scheduler.sort_tasks_by_priority_due(tasks)

    assert [t.id for t in ordered] == ["s1", "s2", "s3"]


def test_recurring_daily_task_generates_next_occurrence():
    task = Task(
        id="test-3",
        title="Daily walk",
        duration_minutes=30,
        priority=5,
        is_recurring=True,
        recurrence_rule="daily",
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=7, minute=0),
    )

    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_time.date() == date.today() + timedelta(days=1)
    assert next_task.is_recurring is True
    assert next_task.completed is False


def test_scheduler_detects_duplicate_time_conflict():
    owner = Owner(name="Alex", available_minutes_per_day=120)
    pet1 = Pet(name="Fido", species="Dog")
    pet2 = Pet(name="Whiskers", species="Cat")
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(
        id="d1",
        title="Breakfast",
        duration_minutes=30,
        priority=4,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=8, minute=0),
    )
    task2 = Task(
        id="d2",
        title="Medication",
        duration_minutes=30,
        priority=4,
        due_time=datetime.combine(date.today(), datetime.min.time()).replace(hour=8, minute=0),
    )

    pet1.add_task(task1)
    pet2.add_task(task2)

    scheduler = Scheduler(owner=owner)
    scheduler.generate_daily_plan(date.today())

    conflicts = scheduler.detect_conflicts(scheduler.scheduled_tasks)
    assert any("overlaps" in c for c in conflicts)
    assert any(c.startswith("WARNING") for c in conflicts)

