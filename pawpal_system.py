from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Tuple, Optional


# ---------------------------------------------------------------------------
# Data Classes — plain objects that hold state
# ---------------------------------------------------------------------------

@dataclass
class Task:
    id: int = 0
    description: str = ""
    duration_mins: int = 15
    priority: str = "medium"      # "high", "medium", "low"
    frequency: str = "once"       # "once", "daily", "weekly"
    due_time: str = ""            # e.g. "09:00"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"

    def next_occurrence(self, current_date: date) -> "Task":
        """Return a new incomplete Task instance due on the next daily or weekly date."""
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_date = current_date + delta
        return Task(
            id=self.id + 1000,
            description=self.description,
            duration_mins=self.duration_mins,
            priority=self.priority,
            frequency=self.frequency,
            due_time=f"{next_date.isoformat()} {self.due_time}",
            is_completed=False,
        )


@dataclass
class Pet:
    id: int = 0
    name: str = ""
    species: str = ""             # e.g. "Dog", "Cat"
    age: int = 0
    health_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks


# ---------------------------------------------------------------------------
# Regular Classes — logic-heavy objects
# ---------------------------------------------------------------------------

class Owner:
    """Represents the pet owner. Absorbs OwnerPreference — preferences live here directly."""

    def __init__(
        self,
        id: int,
        name: str,
        email: str,
        available_hours: float,
        preferred_feeding_time: str = "",
        preferred_walk_time: str = "",
        times_to_avoid: Optional[List[str]] = None,
        max_tasks_per_session: int = 3,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.available_hours = available_hours
        # Preference fields (previously a separate OwnerPreference class)
        self.preferred_feeding_time = preferred_feeding_time  # e.g. "08:00"
        self.preferred_walk_time = preferred_walk_time        # e.g. "07:00"
        self.times_to_avoid: List[str] = times_to_avoid or []
        self.max_tasks_per_session = max_tasks_per_session
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def request_daily_plan(self) -> "Scheduler":
        """Instantiate a Scheduler for this owner and return it after generating a plan."""
        scheduler = Scheduler(self)
        scheduler.generate_plan()
        return scheduler


class Scheduler:
    """
    Core logic class. Absorbs Planner, DailyPlan, ScheduledTask, Constraint,
    and ExplanationEngine into one place.

    The schedule is stored as a list of (Pet, Task, start_time, end_time) tuples.
    Skipped tasks are tracked separately so the explanation methods can reference them.
    """

    def __init__(self, owner: Owner):
        self.owner = owner
        self.pets: List[Pet] = owner.pets
        # schedule entries: (pet, task, start_time, end_time)
        self.schedule: List[Tuple[Pet, Task, str, str]] = []
        self.skipped_tasks: List[Task] = []  # tasks considered but not scheduled

    # --- Plan generation ---

    def _collect_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet, task))
        return all_tasks

    def generate_plan(self) -> None:
        """Build the schedule by prioritizing tasks and checking constraints."""
        all_pairs = self._collect_all_tasks()
        # Separate pets from tasks, prioritize, then re-pair
        pet_lookup = {id(task): pet for pet, task in all_pairs}
        tasks = self.prioritize_tasks([task for _, task in all_pairs])

        current_minutes = 8 * 60  # start at 08:00
        available_minutes = self.owner.available_hours * 60

        for task in tasks:
            if current_minutes + task.duration_mins > 8 * 60 + available_minutes:
                self.skipped_tasks.append(task)
                continue
            start = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
            current_minutes += task.duration_mins
            end = f"{current_minutes // 60:02d}:{current_minutes % 60:02d}"
            self.schedule.append((pet_lookup[id(task)], task, start, end))

    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by priority (high → medium → low)."""
        order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: order.get(t.priority, 1))

    def check_constraints(self, task: Task, proposed_start: str) -> bool:
        """Return True if the task can be scheduled at proposed_start given the owner's time limits and avoided slots."""
        pass

    def sort_by_time(self) -> List[Tuple[Pet, Task, str, str]]:
        """Return schedule entries sorted by start_time in HH:MM order."""
        return sorted(self.schedule, key=lambda entry: entry[2])

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Tuple[Pet, Task, str, str]]:
        """Return schedule entries filtered by pet name and/or completion status."""
        result = self.schedule
        if pet_name is not None:
            result = [e for e in result if e[0].name.lower() == pet_name.lower()]
        if completed is not None:
            result = [e for e in result if e[1].is_completed == completed]
        return result

    def detect_conflicts(self) -> List[str]:
        """Return a list of warning strings for any two schedule entries whose time slots overlap."""
        warnings = []
        entries = self.schedule
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                pet_a, task_a, start_a, end_a = entries[i]
                pet_b, task_b, start_b, end_b = entries[j]
                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"CONFLICT: '{task_a.description}' ({pet_a.name}, {start_a}–{end_a}) "
                        f"overlaps '{task_b.description}' ({pet_b.name}, {start_b}–{end_b})"
                    )
        return warnings

    def spawn_recurring(self, pet: Pet, task: Task) -> None:
        """If task is recurring, mark it complete and add the next occurrence to the pet's task list."""
        task.mark_complete()
        if task.frequency in ("daily", "weekly"):
            pet.add_task(task.next_occurrence(date.today()))

    # --- Plan output ---

    def get_summary(self) -> str:
        """Return a human-readable summary of the scheduled plan."""
        lines = [f"Today's Schedule for {self.owner.name}", "=" * 40]
        for pet, task, start, end in self.schedule:
            status = "✓" if task.is_completed else "○"
            lines.append(f"  {status} [{start}–{end}] {pet.name}: {task.description} ({task.priority} priority)")
        if self.skipped_tasks:
            lines.append("\nSkipped (not enough time):")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.description}")
        lines.append(f"\nTotal tasks scheduled: {len(self.schedule)}")
        return "\n".join(lines)

    # --- Explanation (previously ExplanationEngine) ---

    def explain_plan(self) -> str:
        """Return a full explanation of why the plan was built this way."""
        pass

    def explain_skipped(self, task: Task) -> str:
        """Return an explanation for why a specific task was skipped or delayed."""
        pass
