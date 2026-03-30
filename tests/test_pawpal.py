from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner(hours=3.0):
    """Return a basic Owner with no pets."""
    return Owner(id=1, name="Alex", email="", available_hours=hours)


def make_pet_with_tasks(*tasks):
    """Return a Pet pre-loaded with the given Task objects."""
    pet = Pet(id=1, name="Buddy", species="Dog", age=3)
    for task in tasks:
        pet.add_task(task)
    return pet


# ---------------------------------------------------------------------------
# Phase 2 tests (existing)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Phase 5 tests — sorting, recurrence, conflict detection, edge cases
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return schedule entries ordered by start time."""
    # Add tasks out of priority order so generate_plan slots them non-trivially
    pet = make_pet_with_tasks(
        Task(id=1, description="Grooming",  duration_mins=20, priority="low",    due_time="10:00"),
        Task(id=2, description="Walk",      duration_mins=30, priority="high",   due_time="07:00"),
        Task(id=3, description="Medication",duration_mins=5,  priority="high",   due_time="08:00"),
    )
    owner = make_owner()
    owner.add_pet(pet)
    scheduler = owner.request_daily_plan()

    sorted_entries = scheduler.sort_by_time()
    start_times = [entry[2] for entry in sorted_entries]
    assert start_times == sorted(start_times), f"Expected sorted times, got {start_times}"


def test_recurring_daily_task_creates_next_occurrence():
    """spawn_recurring() on a daily task should add a new task due the following day."""
    today = date.today()
    expected_date = (today + timedelta(days=1)).isoformat()

    task = Task(id=1, description="Morning walk", duration_mins=30,
                priority="high", frequency="daily", due_time="07:00")
    pet = make_pet_with_tasks(task)
    owner = make_owner()
    owner.add_pet(pet)
    scheduler = owner.request_daily_plan()

    scheduler.spawn_recurring(pet, task)

    # Original task should now be marked complete
    assert task.is_completed is True
    # A new task should have been appended with tomorrow's date in due_time
    new_tasks = [t for t in pet.get_tasks() if t.id == task.id + 1000]
    assert len(new_tasks) == 1
    assert expected_date in new_tasks[0].due_time


def test_conflict_detection_flags_overlapping_slots():
    """detect_conflicts() should return at least one warning when two entries overlap."""
    pet = make_pet_with_tasks(
        Task(id=1, description="Walk", duration_mins=30, priority="high")
    )
    owner = make_owner()
    owner.add_pet(pet)
    scheduler = owner.request_daily_plan()

    # Manually inject an overlapping entry
    overlap_task = Task(id=99, description="Vet call", duration_mins=20, priority="high")
    scheduler.schedule.append((pet, overlap_task, "08:10", "08:30"))

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0
    assert "CONFLICT" in conflicts[0]


def test_no_conflict_when_slots_are_sequential():
    """detect_conflicts() should return an empty list when tasks are back-to-back."""
    pet = make_pet_with_tasks(
        Task(id=1, description="Walk",    duration_mins=30, priority="high"),
        Task(id=2, description="Feeding", duration_mins=10, priority="high"),
    )
    owner = make_owner()
    owner.add_pet(pet)
    scheduler = owner.request_daily_plan()

    # generate_plan sequences tasks without overlap by design
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


def test_empty_schedule_for_pet_with_no_tasks():
    """A pet with no tasks should produce an empty schedule with no errors."""
    pet = Pet(id=1, name="Ghost", species="Cat", age=2)  # no tasks added
    owner = make_owner()
    owner.add_pet(pet)
    scheduler = owner.request_daily_plan()

    assert scheduler.schedule == []
    assert scheduler.skipped_tasks == []
