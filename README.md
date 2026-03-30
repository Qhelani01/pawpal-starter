# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test | Behaviour verified |
|---|---|
| `test_task_completion` | `mark_complete()` flips `is_completed` to `True` |
| `test_pet_task_addition` | `add_task()` increases the pet's task count |
| `test_sort_by_time_returns_chronological_order` | `sort_by_time()` returns entries in HH:MM order |
| `test_recurring_daily_task_creates_next_occurrence` | `spawn_recurring()` appends a new task due the next day |
| `test_conflict_detection_flags_overlapping_slots` | `detect_conflicts()` catches overlapping time windows |
| `test_no_conflict_when_slots_are_sequential` | Back-to-back tasks produce zero conflicts |
| `test_empty_schedule_for_pet_with_no_tasks` | A pet with no tasks generates an empty schedule safely |

**Confidence level: ★★★★☆** — Core scheduling behaviours (prioritisation, recurring tasks, conflict detection, sorting, filtering) are all covered. Edge cases like overlapping slots and empty pets pass. Untested areas include constraint checking and multi-day recurring plans.

## Features

| Feature | Description |
|---|---|
| **Owner & pet setup** | Enter owner name, available hours, pet name, and species |
| **Task management** | Add tasks with title, duration, priority, and due time |
| **Priority scheduling** | High-priority tasks are always scheduled first |
| **Sorting by time** | Schedule is displayed in chronological start-time order |
| **Conflict warnings** | Overlapping time slots are flagged with `⚠ CONFLICT` messages |
| **Daily recurrence** | Recurring tasks auto-generate the next occurrence when completed |
| **Skipped task tracking** | Tasks that don't fit the available time are listed separately |

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Demo

<a href="course_images/ai110/pawpal_demo.png" target="_blank"><img src="course_images/ai110/pawpal_demo.png" alt="PawPal+ schedule screenshot" width="700"/></a>

> Run `streamlit run app.py`, add a few tasks, then click **Generate schedule** to see the sorted plan, conflict warnings, and skipped-task summary.
