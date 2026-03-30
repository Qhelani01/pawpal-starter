from pawpal_system import Task, Pet, Owner

# --- Setup ---
owner = Owner(
    id=1,
    name="Alex",
    email="alex@email.com",
    available_hours=3,
    preferred_feeding_time="08:00",
    preferred_walk_time="07:00",
    times_to_avoid=["12:00"],
)

buddy = Pet(id=1, name="Buddy", species="Dog", age=3)
whiskers = Pet(id=2, name="Whiskers", species="Cat", age=5)

buddy.add_task(Task(id=1, description="Morning walk",      duration_mins=30, priority="high",   frequency="daily",  due_time="07:00"))
buddy.add_task(Task(id=2, description="Breakfast feeding", duration_mins=10, priority="high",   frequency="daily",  due_time="08:00"))
buddy.add_task(Task(id=3, description="Grooming session",  duration_mins=20, priority="low",    frequency="weekly", due_time="10:00"))
whiskers.add_task(Task(id=4, description="Medication",     duration_mins=5,  priority="high",   frequency="daily",  due_time="08:00"))  # same slot as Buddy's feeding — triggers conflict
whiskers.add_task(Task(id=5, description="Playtime",       duration_mins=15, priority="medium", frequency="once",   due_time="09:00"))

owner.add_pet(buddy)
owner.add_pet(whiskers)

scheduler = owner.request_daily_plan()

# --- 1. Base schedule ---
print(scheduler.get_summary())

# --- 2. Sort by time ---
print("\n--- Sorted by start time ---")
for pet, task, start, end in scheduler.sort_by_time():
    print(f"  [{start}–{end}] {pet.name}: {task.description}")

# --- 3. Filter by pet and by status ---
print("\n--- Buddy's tasks only ---")
for pet, task, start, end in scheduler.filter_tasks(pet_name="Buddy"):
    print(f"  [{start}–{end}] {task.description}")

print("\n--- Incomplete tasks only ---")
for pet, task, start, end in scheduler.filter_tasks(completed=False):
    print(f"  [{start}–{end}] {pet.name}: {task.description}")

# --- 4. Conflict detection ---
# Inject an overlapping entry to simulate a manually added task that clashes
overlapping = Task(id=99, description="Vet call", duration_mins=20, priority="high", due_time="08:10")
scheduler.schedule.append((buddy, overlapping, "08:10", "08:30"))

print("\n--- Conflict detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠ {warning}")
else:
    print("  No conflicts found.")

# --- 5. Recurring task: mark Buddy's walk complete and spawn next occurrence ---
print("\n--- Recurring task: complete Buddy's morning walk ---")
walk_entry = next((e for e in scheduler.schedule if e[1].description == "Morning walk"), None)
if walk_entry:
    pet, task, _, _ = walk_entry
    scheduler.spawn_recurring(pet, task)
    print(f"  '{task.description}' marked complete. Next occurrence added:")
    recurring = [t for t in buddy.get_tasks() if t.id == task.id + 1000]
    if recurring:
        print(f"  -> Due: {recurring[0].due_time}")
