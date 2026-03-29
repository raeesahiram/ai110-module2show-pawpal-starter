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

    # Configure and run scheduler
    scheduler = Scheduler(owner=owner)
    scheduler.generate_daily_plan(date.today())

    # Print schedule
    print("Today's Schedule")
    print("====================")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()