from datetime import datetime, date

from pawpal_system import Task, Pet


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
