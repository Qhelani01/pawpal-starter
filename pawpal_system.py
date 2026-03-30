from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data Classes — plain objects that hold state
# ---------------------------------------------------------------------------

@dataclass
class OwnerPreference:
    preferred_feeding_time: str = ""          # e.g. "08:00"
    preferred_walk_time: str = ""             # e.g. "07:00"
    times_to_avoid: List[str] = field(default_factory=list)   # e.g. ["12:00", "15:00"]
    max_tasks_per_session: int = 3

    def get_preferred_times(self) -> List[str]:
        """Return a list of the owner's preferred task times."""
        pass

    def get_times_to_avoid(self) -> List[str]:
        """Return the list of times the owner wants to avoid."""
        pass


@dataclass
class Constraint:
    type: str = ""                # e.g. "time_window", "deadline", "medication"
    description: str = ""
    time_window: str = ""         # e.g. "08:00-09:00"
    is_required: bool = False

    def is_satisfied(self, task: "PetCareTask") -> bool:
        """Return True if this constraint is satisfied for the given task."""
        pass

    def get_time_window(self) -> str:
        """Return the constraint's time window string."""
        pass


@dataclass
class PetCareTask:
    id: int = 0
    description: str = ""
    duration_mins: int = 15
    priority: str = "medium"      # "high", "medium", "low"
    frequency: str = "once"       # "once", "daily", "weekly"
    due_time: str = ""            # e.g. "09:00"
    is_completed: bool = False
    constraints: List[Constraint] = field(default_factory=list)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        pass


@dataclass
class Pet:
    id: int = 0
    name: str = ""
    species: str = ""             # e.g. "Dog", "Cat"
    age: int = 0
    health_notes: str = ""
    tasks: List[PetCareTask] = field(default_factory=list)

    def add_task(self, task: PetCareTask) -> None:
        """Add a care task to this pet."""
        pass

    def get_tasks(self) -> List[PetCareTask]:
        """Return all tasks associated with this pet."""
        pass


@dataclass
class ScheduledTask:
    task: Optional[PetCareTask] = None
    start_time: str = ""          # e.g. "09:00"
    end_time: str = ""            # e.g. "09:30"
    status: str = "pending"       # "pending", "completed"

    def get_duration(self) -> int:
        """Return the duration of the task in minutes."""
        pass

    def mark_complete(self) -> None:
        """Mark this scheduled task as completed."""
        pass

    def is_completed(self) -> bool:
        """Return True if this scheduled task is completed."""
        pass


@dataclass
class DailyPlan:
    date: str = ""                # e.g. "2026-03-29"
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    total_time_used: float = 0.0  # in minutes

    def add_task(self, task: ScheduledTask) -> None:
        """Add a scheduled task to the plan."""
        pass

    def get_total_time(self) -> float:
        """Return the total time used by all scheduled tasks."""
        pass

    def get_summary(self) -> str:
        """Return a human-readable summary of the daily plan."""
        pass


# ---------------------------------------------------------------------------
# Regular Classes — logic-heavy objects
# ---------------------------------------------------------------------------

class PetOwner:
    def __init__(self, id: int, name: str, email: str, available_hours: float):
        self.id = id
        self.name = name
        self.email = email
        self.available_hours = available_hours
        self.pets: List[Pet] = []
        self.preferences: Optional[OwnerPreference] = None

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        pass

    def request_daily_plan(self) -> DailyPlan:
        """Trigger the Planner to generate a daily plan for this owner."""
        pass


class Planner:
    def __init__(self, owner: PetOwner):
        self.owner = owner
        self.pets: List[Pet] = owner.pets
        self.constraints: List[Constraint] = []

    def generate_daily_plan(self) -> DailyPlan:
        """Generate and return a DailyPlan by prioritizing tasks and checking constraints."""
        pass

    def prioritize_tasks(self, tasks: List[PetCareTask]) -> List[PetCareTask]:
        """Return tasks sorted by priority (high → medium → low)."""
        pass

    def check_constraints(self, task: PetCareTask) -> bool:
        """Return True if all constraints are satisfied for the given task."""
        pass


class ExplanationEngine:
    def __init__(self, plan: DailyPlan):
        self.plan = plan

    def explain_plan(self) -> str:
        """Return a full explanation of why the plan was built this way."""
        pass

    def explain_delay(self, task: PetCareTask) -> str:
        """Return an explanation for why a specific task was delayed or skipped."""
        pass

    def summarize_reasoning(self) -> str:
        """Return a short summary of the key scheduling decisions."""
        pass
