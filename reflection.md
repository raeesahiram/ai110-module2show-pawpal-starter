# PawPal+ Project Reflection

## 1. System Design
- 1. The user should be able to add and remove pets from their account.
- 2. The user should be able to see their daily tasks on the home screen when they open the app.
- 3. The user should be able to schedule walks on a calendar for the future.

**a. Initial design**

- Briefly describe your initial UML design.
1. The initial UML design uses four core classes in a straightforward domain model. Owner holds the user’s identity, timezone, daily available minutes, and a list of pets, and it manages high-level ownership state. Pet encapsulates a single animal’s profile data plus a task list and the ability to manage that list. Task captures a specific care action with duration, priority, scheduling rules, due date, and completion state, and it includes methods to update status and decide whether it should run on a given day. Scheduler is responsible for taking an owner’s pets and tasks, selecting candidate tasks for a date, ordering them by priority/due constraints, fitting them into availability, producing the daily plan, and explaining conflicts or decisions.

- What classes did you include, and what responsibilities did you assign to each?
1. Owner - Responsibility: model the pet owner and global daily constraints
2. Pet - Responsibility: represent a single pet with its profile and task list
3. Task (dataclass) - Responsibility: represent one care activity with schedule metadata and completion state
4. Scheduler - Responsibility: build/maintain a daily task plan for owner/pets under constraints


**b. Design changes**

- Did your design change during implementation?
1. The Scheduler class was updated to include a real conflict detection method instead of leaving it as a placeholder.
- detect_conflicts(self, tasks: List[Task]) now checks:
- - if total scheduled minutes exceed owner’s daily availability,
- - if there are duplicate task IDs,
- - if any single task duration exceeds the owner’s entire daily window.
- explain_plan now calls detect_conflicts, and appends conflicts to the human-readable schedule summary including total minutes and remaining slack.

- If yes, describe at least one change and why you made it.
1. This was introduced because the earlier design had a functional gap: the pipeline could schedule tasks but not flag impossible or inconsistent states. Detecting oversubscription guards against generating plans that exceed user constraints. Duplicate ID detection guards against corrupted task sets and helps diagnose data integrity problems. Single-task duration checks help surface unschedulable task definitions early (instead of silently dropping them or producing confusing results). In practical terms, separating conflict checks means the scheduler can now report “why” a given plan is invalid, which supports reliable behavior, debugging, and user transparency.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
Time availability (Owner.available_minutes_per_day)
total daily capacity is enforced by fit_tasks_by_availability
excess workload is flagged in detect_conflicts
Task duration
tasks with duration_minutes <= 0 are skipped
tasks with duration > daily capacity are flagged as unschedulable
Priority
sorted first in sort_tasks_by_priority_due so high-priority tasks are considered first
Due date / schedule day
Task.should_run_today checks due_time date and recurrence rule
Recurrence
Task.is_recurring + recurrence_rule influences eligibility
mark_completed can create next-day/week instance
Completion state
completed tasks are excluded from today’s plan
Conflict constraints
duplicate task IDs
time overlaps (same or conflicting windows) flagged as warnings

- How did you decide which constraints mattered most?
Start with the core user promise: “Produce a reliable daily plan that fits owner availability.”
so time budget (available minutes, task duration) is primary
Next, enforce meaning/value through priority
schedule most impactful tasks first
Add correctness safety checks (preferred by UI trust)
detect duplicate IDs and impossible tasks, provide non-crash warnings
Lastly, support real reuse via recurring tasks
recurring tasks should continue automatically and not require re-entry each day

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
1. Current conflict detection primarily checks for tasks that start at the same time, which is simple and performant, but it sacrifices capturing partial overlaps.
- Why is that tradeoff reasonable for this scenario?
1. It is easy to reason about and fast (linear or near-linear complexity) but might miss more subtle overlaps (e.g., A: 10:00-10:30, B: 10:15-10:45) if not fully normalized. It also applies well to “slot-based” data but less to continuous flexible timing.


---

## 3. AI Collaboration

**a. How you used AI**

I used AI as an iterative coding partner for design, debugging, and refactoring. I asked for behaviors that matched requirements (sorting, recurrence, conflict warnings), then implemented and validated the suggestions. Prompting for concrete code examples plus tests was especially helpful because it made outputs directly usable. It also helped to keep architecture consistent between `pawpal_system.py` and `app.py`.

**b. Judgment and verification**

One moment where I did not accept AI as-is was when a suggestion for an optimal knapsack-style scheduler appeared; I felt that was overkill for the project scope. Instead, I chose a deterministic greedy solution and wrote targeted tests to validate it. I used `pytest` assertions and manual Streamlit runs to verify correctness before accepting the final design.

---

## 4. Testing and Verification

**a. What you tested**

I tested task sorting order, recurrence behavior, conflict detection, and edge cases like no pets/no tasks. These tests were important to ensure the app behaves predictably and that users can trust schedule output. Strong test coverage also made refactoring safer as I added features.

**b. Confidence**

I am confident (5/5) that the scheduler works for the current scope because all `pytest` tests pass and behavior matches the requirements. With more time, I would add temporal edge cases (cross-day recurrence, timezone effects, partial overlaps) and UI integration tests for the Streamlit workflow.

---

## 5. Reflection

**a. What went well**

The scheduler architecture and clear class responsibilities worked well; implementing recurring tasks plus conflict warnings was a big success. The integration with Streamlit UI also came together cleanly.

**b. What you would improve**

Next iteration I’d improve the overlap detection to handle partial intervals exactly and introduce a slot-based time allocation model. I’d also add persistent state (database or local storage) so tasks survive reloads.

**c. Key takeaway**

I learned that a pragmatic algorithm with good tests and a non-crashing warning model is usually better than chasing perfect optimization early. Working with AI effectively means iterating and validating, not blindly accepting every suggestion.
