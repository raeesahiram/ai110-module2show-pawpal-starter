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

## Smarter Scheduling

PawPal+ now includes enhanced scheduling features in `pawpal_system.py`:

- Recurring task support: `Task.mark_completed()` auto-generates the next `daily` or `weekly` task occurrence using `timedelta`.
- Filter tasks by `completed` and `pet_name` via `Owner.get_tasks(completed, pet_name)`.
- Greedy daily plan generation with priority-based sorting and availability fit (`Scheduler.generate_daily_plan`).
- Non-fatal conflict detection with warnings for:
  - over-capacity workload,
  - duplicate task IDs,
  - per-task duration > daily availability,
  - overlapping timed tasks (same or conflicting time ranges).
- `scheduler.explain_plan()` includes conflicts as warning entries instead of crashing.

## Testing PawPal+

Run tests with:

```bash
python -m pytest
```

Current test coverage focuses on:

- sorting correctness (`Scheduler.sort_tasks_by_priority_due`) and chronological order behavior
- recurrence logic (`Task.mark_completed`) for daily roll-forward tasks
- conflict detection (`Scheduler.detect_conflicts`) for overlapping times and duplicate/residual constraints
- base cases including no-pets and no-tasks

### Confidence Level

- ★★★★★ (5/5) based on the current suite passing all designed behaviors and edge-cases in local test runs.

