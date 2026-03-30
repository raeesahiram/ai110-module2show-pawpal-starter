import streamlit as st
from datetime import date, datetime
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

if "owner" not in st.session_state or not isinstance(st.session_state.owner, Owner):
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=120)

owner = st.session_state.owner

# Add pet UI
st.markdown("### Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="")
age = st.number_input("Age", min_value=0, max_value=30, value=1)

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species, breed=breed or None, age=int(age))
    owner.add_pet(new_pet)
    st.success(f"Added pet: {new_pet.name}")

if owner.pets:
    st.write("### Current pets")
    st.table([{"name": p.name, "species": p.species, "breed": p.breed, "age": p.age} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

# Add task UI
st.markdown("### Add a Task")
if not owner.pets:
    st.warning("Please add a pet before adding tasks.")
else:
    pet_selection = st.selectbox("Assign to pet", [p.name for p in owner.pets])
    task_title = st.text_input("Task title", value="Morning walk")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=4)

    if st.button("Add task"):
        selected_pet = next(p for p in owner.pets if p.name == pet_selection)
        new_task = Task(
            id=f"{pet_selection}-{len(selected_pet.tasks)+1}",
            title=task_title,
            duration_minutes=int(duration),
            priority=int(priority),
        )
        selected_pet.add_task(new_task)
        st.success(f"Added task to {selected_pet.name}: {new_task.title}")

    st.write("### Current tasks per pet")
    for pet in owner.pets:
        st.write(f"**{pet.name}**")
        if pet.tasks:
            st.table([{"id": t.id, "title": t.title, "duration": t.duration_minutes, "priority": t.priority, "completed": t.completed} for t in pet.tasks])
        else:
            st.info(f"{pet.name} has no tasks yet.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button now calls your scheduling logic.")

from pawpal_system import Scheduler

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Add at least one pet before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        scheduler.generate_daily_plan(date.today())

        # Display schedule summary
        st.write("### Today's Schedule")
        st.success("Schedule generated successfully")

        conflicts = scheduler.detect_conflicts(scheduler.scheduled_tasks)
        if conflicts:
            st.warning("Potential schedule conflicts detected. Please review the task timings below.")
            for warning_text in conflicts:
                st.warning(warning_text)

        plan_table = [
            {
                "Task": task.title,
                "Pet": next((pet.name for pet in owner.pets if task in pet.tasks), "Unknown"),
                "Duration": task.duration_minutes,
                "Priority": task.priority,
                "Due": task.due_time.strftime("%H:%M") if task.due_time else "n/a",
            }
            for task in scheduler.get_schedule()
        ]

        if plan_table:
            st.table(plan_table)
        else:
            st.info("No tasks fit the schedule for today.")

        # Show pending tasks sorted by due time as additional view
        pending = owner.get_tasks(completed=False)
        sorted_pending = sorted(
            pending,
            key=lambda t: t.due_time if t.due_time is not None else datetime.max,
        )
        if sorted_pending:
            st.write("### Pending tasks (sorted)")
            st.table(
                [
                    {
                        "Task": t.title,
                        "Pet": next((pet.name for pet in owner.pets if t in pet.tasks), "Unknown"),
                        "Due": t.due_time.strftime("%H:%M") if t.due_time else "n/a",
                        "Priority": t.priority,
                    }
                    for t in sorted_pending
                ]
            )
        else:
            st.info("No pending tasks available.")

        # Explain plan text for users who want details
        st.write("### Detailed Plan Explanation")
        st.text(scheduler.explain_plan())

