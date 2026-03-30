import streamlit as st
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A pet care planning assistant.")

# ---------------------------------------------------------------------------
# Step 1 — Owner & pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_hours = st.number_input(
        "Available hours today", min_value=0.5, max_value=12.0, value=3.0, step=0.5
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["Dog", "Cat", "Other"])

# ---------------------------------------------------------------------------
# Step 2 — Session state: keep the Owner alive across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    pet = Pet(id=1, name=pet_name, species=species)
    owner = Owner(id=1, name=owner_name, email="", available_hours=available_hours)
    owner.add_pet(pet)
    st.session_state.owner = owner

# Always read from session state so edits to the form take effect on Reset
owner: Owner = st.session_state.owner
pet: Pet = owner.pets[0]

if st.button("Reset owner & pet"):
    del st.session_state.owner
    st.rerun()

# ---------------------------------------------------------------------------
# Step 3 — Add a task: wired to pet.add_task()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (mins)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    due_time = st.text_input("Due time (HH:MM)", value="08:00")

if st.button("Add task"):
    task_id = len(pet.get_tasks()) + 1
    pet.add_task(
        Task(
            id=task_id,
            description=task_title,
            duration_mins=int(duration),
            priority=priority,
            due_time=due_time,
        )
    )
    st.success(f"'{task_title}' added to {pet.name}'s task list.")

# Show current task list
if pet.get_tasks():
    st.write(f"**{pet.name}'s tasks ({len(pet.get_tasks())} total):**")
    st.table(
        [
            {
                "Task": t.description,
                "Duration (mins)": t.duration_mins,
                "Priority": t.priority,
                "Due": t.due_time,
                "Done": "✓" if t.is_completed else "○",
            }
            for t in pet.get_tasks()
        ]
    )
else:
    st.info("No tasks yet — add one above.")

# ---------------------------------------------------------------------------
# Step 4 — Generate schedule with sorting and conflict detection
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if not pet.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner.available_hours = available_hours
        scheduler = owner.request_daily_plan()

        # --- Sorted schedule table ---
        st.success("Schedule generated!")
        sorted_entries = scheduler.sort_by_time()
        if sorted_entries:
            st.table(
                [
                    {
                        "Start": start,
                        "End": end,
                        "Pet": p.name,
                        "Task": t.description,
                        "Priority": t.priority,
                        "Status": "✓ Done" if t.is_completed else "○ Pending",
                    }
                    for p, t, start, end in sorted_entries
                ]
            )
        else:
            st.info("No tasks fit within the available time.")

        # --- Skipped tasks ---
        if scheduler.skipped_tasks:
            st.warning(
                "**Skipped (not enough time):** "
                + ", ".join(t.description for t in scheduler.skipped_tasks)
            )

        # --- Conflict detection ---
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.subheader("⚠ Conflicts Detected")
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts found.")
