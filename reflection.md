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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
