from pawpal_system import Task, Pet


def test_task_completion():
    """Calling mark_complete() should set is_completed to True."""
    task = Task(id=1, description="Morning walk", duration_mins=30, priority="high")
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_pet_task_addition():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet(id=1, name="Buddy", species="Dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(id=1, description="Feeding", duration_mins=10, priority="high"))
    assert len(pet.get_tasks()) == 1
