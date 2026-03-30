from pawpal_system import Task, Pet, Owner

# --- Create owner ---
owner = Owner(
    id=1,
    name="Alex",
    email="alex@email.com",
    available_hours=3,
    preferred_feeding_time="08:00",
    preferred_walk_time="07:00",
    times_to_avoid=["12:00"],
)

# --- Create pets ---
buddy = Pet(id=1, name="Buddy", species="Dog", age=3)
whiskers = Pet(id=2, name="Whiskers", species="Cat", age=5)

# --- Add tasks to Buddy ---
buddy.add_task(Task(id=1, description="Morning walk",     duration_mins=30, priority="high",   due_time="07:00"))
buddy.add_task(Task(id=2, description="Breakfast feeding", duration_mins=10, priority="high",   due_time="08:00"))
buddy.add_task(Task(id=3, description="Grooming session", duration_mins=20, priority="low",    due_time="10:00"))

# --- Add tasks to Whiskers ---
whiskers.add_task(Task(id=4, description="Medication",    duration_mins=5,  priority="high",   due_time="08:30"))
whiskers.add_task(Task(id=5, description="Playtime",      duration_mins=15, priority="medium", due_time="09:00"))

# --- Register pets with owner ---
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Generate and print the plan ---
scheduler = owner.request_daily_plan()
print(scheduler.get_summary())
