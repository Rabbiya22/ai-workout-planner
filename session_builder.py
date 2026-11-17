
import heapq
from itertools import count

from exercise_filter import load_exercises
from weekly_split import dfs_split, DAY_NAMES
from plan_checker import (
    check_R0,
    get_age_message,
    check_plan,
    MAX_SESSION_MINUTES,
    ALLOWED_EQUIPMENT
)

SETS = 3

# Fixed project settings (not customer inputs)
PROJECT_LEVEL = "beginner"
PROJECT_EQUIPMENT = ALLOWED_EQUIPMENT

LEVELS = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}


# --------------------------------------------------
# 1. COLLECT CUSTOMER AGE
# --------------------------------------------------

def get_customer_profile():

    print("\n========== AI WORKOUT PLANNER ==========")

    while True:
        try:
            age = int(input("\nEnter your age: "))

            profile = {"age": age}

            if check_R0(profile):
                print(get_age_message(age))
                return profile

            print(get_age_message(age))
            return None

        except ValueError:
            print("Please enter a valid whole number.")


# --------------------------------------------------
# 2. COLLECT CUSTOMER'S PREFERRED GYM DAYS
# --------------------------------------------------

def get_user_availability():

    print("\n========== CHOOSE YOUR GYM DAYS ==========")

    print("\nAvailable days:")
    print("Monday, Tuesday, Wednesday, Thursday, Friday, Saturday")
    print("Sunday is a holiday.")

    valid_days = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5
    }

    while True:

        entered_days = input(
            "\nEnter your preferred days separated by commas: "
        )

        day_names = [
            day.strip().lower()
            for day in entered_days.split(",")
            if day.strip()
        ]

        if not day_names:
            print("Please select at least one day.")
            continue

        if any(day not in valid_days for day in day_names):
            print("Invalid day. Choose Monday to Saturday.")
            continue

        if len(day_names) != len(set(day_names)):
            print("You cannot select the same day twice.")
            continue

        selected_days = sorted(
            valid_days[day] for day in day_names
        )

        available_days = len(selected_days)

        return available_days, selected_days


# --------------------------------------------------
# 3. PREPARE EXERCISE DATA
# --------------------------------------------------

def prepare_exercise(exercise):

    exercise = dict(exercise)

    exercise["id"] = (
        exercise.get("id")
        or exercise.get("exercise_id")
        or exercise["name"]
    )

    exercise["minutes_per_set"] = float(
        exercise["minutes_per_set"]
    )

    exercise["primary_muscle"] = (
        exercise["primary_muscle"].strip().lower()
    )

    secondary = exercise.get("secondary_muscles", [])

    if isinstance(secondary, str):
        secondary = secondary.replace(",", ";").split(";")

    exercise["secondary_muscles"] = [
        muscle.strip().lower()
        for muscle in secondary
        if muscle and muscle.strip()
    ]

    exercise["equipment"] = (
        exercise["equipment"].strip().lower()
    )

    exercise["level"] = (
        exercise["level"].strip().lower()
    )

    return exercise


# --------------------------------------------------
# 4. CHECK EQUIPMENT AND EXERCISE LEVEL
# --------------------------------------------------

def is_suitable_exercise(exercise):

    # R1: Check project equipment availability

    if exercise["equipment"] not in PROJECT_EQUIPMENT:
        return False

    # R2: Exercise difficulty must not exceed project level

    user_level = LEVELS[PROJECT_LEVEL]

    exercise_level = LEVELS.get(
        exercise["level"],
        0
    )

    if exercise_level == 0 or exercise_level > user_level:
        return False

    return True


# --------------------------------------------------
# 5. CALCULATE EXERCISE TIME
# --------------------------------------------------

def exercise_time(exercise):

    return float(exercise["minutes_per_set"]) * SETS


# --------------------------------------------------
# 6. IDENTIFY ACTIVE MUSCLES
# --------------------------------------------------

def get_active_muscles(exercise):

    muscles = {exercise["primary_muscle"]}

    muscles.update(
        exercise.get("secondary_muscles", [])
    )

    return muscles


# --------------------------------------------------
# 7. A* WORKOUT SESSION BUILDER
# --------------------------------------------------

def build_session(
    exercises,
    target_muscles,
    blocked_muscles=None
):

    if blocked_muscles is None:
        blocked_muscles = set()

    candidates = {}

    for muscle in target_muscles:

        candidates[muscle] = [
            ex for ex in exercises
            if ex["primary_muscle"] == muscle
            and is_suitable_exercise(ex)
            and get_active_muscles(ex).isdisjoint(
                blocked_muscles
            )
        ]

        if not candidates[muscle]:
            print("No suitable exercise found for:", muscle)
            return None

    # A* heuristic

    def heuristic(index):

        remaining_time = 0

        for muscle in target_muscles[index:]:

            remaining_time += min(
                exercise_time(ex)
                for ex in candidates[muscle]
            )

        return remaining_time

    queue = []
    counter = count()

    heapq.heappush(
        queue,
        (heuristic(0), 0, next(counter), 0, [])
    )

    while queue:

        estimated_cost, total_time, _, index, selected = (
            heapq.heappop(queue)
        )

        if index == len(target_muscles):
            return selected

        muscle = target_muscles[index]

        for exercise in candidates[muscle]:

            cost = exercise_time(exercise)
            new_time = total_time + cost

            # R3: Check session time

            if new_time > MAX_SESSION_MINUTES:
                continue

            # R5: No repeated exercise in the same session

            if any(
                ex["id"] == exercise["id"]
                for ex in selected
            ):
                continue

            new_selected = selected + [exercise]

            new_estimate = (
                new_time + heuristic(index + 1)
            )

            heapq.heappush(
                queue,
                (
                    new_estimate,
                    new_time,
                    next(counter),
                    index + 1,
                    new_selected
                )
            )

    return None


# --------------------------------------------------
# 8. RECOVERY DEBUGGING
# --------------------------------------------------

def debug_recovery(plan):

    print("\n========== RECOVERY CHECK DETAILS ==========\n")

    sorted_plan = sorted(
        plan,
        key=lambda day: day["day_index"]
    )

    for i in range(len(sorted_plan) - 1):

        today = sorted_plan[i]
        tomorrow = sorted_plan[i + 1]

        if tomorrow["day_index"] != today["day_index"] + 1:
            continue

        today_muscles = set()
        tomorrow_muscles = set()

        for exercise in today["exercises"]:
            today_muscles.update(get_active_muscles(exercise))

        for exercise in tomorrow["exercises"]:
            tomorrow_muscles.update(get_active_muscles(exercise))

        overlap = today_muscles.intersection(
            tomorrow_muscles
        )

        print(
            DAY_NAMES[today["day_index"]],
            "and",
            DAY_NAMES[tomorrow["day_index"]]
        )

        print("Overlapping muscles:", overlap)
        print()


# --------------------------------------------------
# 9. MAIN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":

    # INPUT 1: AGE

    profile = get_customer_profile()

    if profile is None:
        raise SystemExit

    # INPUT 2: PREFERRED GYM DAYS

    available_days, preferred_days = get_user_availability()

    profile["available_days"] = available_days

    # Fixed project settings for the checker

    profile["level"] = PROJECT_LEVEL
    profile["equipment"] = PROJECT_EQUIPMENT
    profile["session_minutes"] = MAX_SESSION_MINUTES

    print("\n========== CUSTOMER PROFILE ==========")

    print("Age:", profile["age"])
    print("Number of selected days:", available_days)

    print("\nYour selected gym days:")

    for day in preferred_days:
        print("-", DAY_NAMES[day])

    # LOAD EXERCISES

    print("\n========== LOADING EXERCISES ==========")

    all_exercises = load_exercises()

    print("Total exercises:", len(all_exercises))

    prepared_exercises = [
        prepare_exercise(exercise)
        for exercise in all_exercises
    ]

    # Apply R1 and R2 before workout generation

    suitable = [
        exercise
        for exercise in prepared_exercises
        if is_suitable_exercise(exercise)
    ]

    print("Suitable exercises:", len(suitable))

    if not suitable:
        print("No suitable exercises found in the dataset.")
        raise SystemExit

    # DFS WEEKLY SPLIT

    weekly_plan = dfs_split(
        available_days,
        preferred_days
    )

    if weekly_plan is None:
        print("No weekly workout split could be generated.")
        raise SystemExit

    print("\n========== WEEKLY WORKOUT SCHEDULE ==========")

    generated_plan = []
    generation_successful = True

    active_by_day = {}

    # Process days in chronological order for R4

    for day, muscles in sorted(weekly_plan.items()):

        print("\n--------------------------------------")
        print(DAY_NAMES[day])
        print("Target muscles:", muscles)

        blocked_muscles = active_by_day.get(
            day - 1,
            set()
        )

        # A* WORKOUT GENERATION

        session = build_session(
            suitable,
            muscles,
            blocked_muscles
        )

        if session is None:

            print("Could not generate a valid session.")
            generation_successful = False
            break

        print("\nA* Workout Session:\n")

        for exercise in session:

            exercise["sets"] = SETS

            print(
                exercise["name"],
                "-",
                SETS,
                "sets"
            )

        total_time = sum(
            exercise_time(exercise)
            for exercise in session
        )

        print(
            "\nEstimated session time:",
            total_time,
            "minutes"
        )

        today_muscles = set()

        for exercise in session:
            today_muscles.update(
                get_active_muscles(exercise)
            )

        active_by_day[day] = today_muscles

        generated_plan.append({
            "day_index": day,
            "exercises": session
        })

    print("\n--------------------------------------")
    print("Sunday: HOLIDAY (GYM CLOSED)")
    print("--------------------------------------")

    if not generation_successful:

        print("\nA complete workout plan could not be generated.")
        print("Check your exercise dataset and weekly split.")

        raise SystemExit

    # --------------------------------------------------
    # 10. VERIFY ALL RULES R0 TO R6
    # --------------------------------------------------

    print("\n========== RECOVERY DETAILS ==========")

    debug_recovery(generated_plan)

    print("\n========== ALL PLAN CHECKER RULES ==========")

    results = check_plan(
        generated_plan,
        profile
    )

    aggregate_keys = {
        "Age_Message",
        "All_Rules_Pass",
        "All_Checked_Rules_Pass"
    }

    for rule, result in results.items():

        if rule in aggregate_keys:
            continue

        if result is True:
            status = "PASS"

        elif result is False:
            status = "FAIL"

        else:
            status = "NOT CHECKED"

        print(rule, ":", status)

    # FINAL APPROVAL

    print("\n========== FINAL PLAN RESULT ==========")

    all_rules_pass = results.get(
        "All_Rules_Pass",
        results.get("All_Checked_Rules_Pass", False)
    )

    if all_rules_pass:

        print("SUCCESS: All rules R0-R6 passed.")
        print("Your workout plan is approved.")

    else:

        print("FAILED: One or more rules did not pass.")
        print("Your workout plan is not approved.")

        for rule, result in results.items():

            if rule.startswith("R") and result is False:
                print("Failed rule:", rule)
