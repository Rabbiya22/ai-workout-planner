
"""
Plan Checker for AI-Based Personalized Workout Planner

Checks all project rules:

R0 - Age Eligibility
R1 - Equipment
R2 - Difficulty Level
R3 - Session Time
R4 - Recovery
R5 - No Repeated Exercises
R6 - Weekly Volume
"""

# ==========================================
# FIXED PROJECT SETTINGS
# ==========================================

MIN_AGE = 19
MAX_AGE = 59

MAX_SESSION_MINUTES = 45

ALLOWED_EQUIPMENT = {
    "bodyweight",
    "bands_other",
    "dumbbell",
    "barbell",
    "machine_cable"
}

ALLOWED_LEVELS = {
    "beginner",
    "intermediate",
    "advanced"
}

LEVEL_RANK = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}

MUSCLE_GROUPS = {
    "chest",
    "back",
    "shoulders",
    "biceps",
    "triceps",
    "quads",
    "hamstrings_glutes",
    "calves",
    "core"
}

# Each muscle must have between 1 and 6 weekly sets
DEFAULT_WEEKLY_SET_LIMITS = {
    muscle: {"min": 1, "max": 6}
    for muscle in MUSCLE_GROUPS
}


# ==========================================
# R0: AGE ELIGIBILITY
# ==========================================

def check_R0(profile):

    age = profile.get("age")

    try:
        age = int(age)
    except (ValueError, TypeError):
        return False

    return MIN_AGE <= age <= MAX_AGE


def get_age_message(age):

    try:
        age = int(age)
    except (ValueError, TypeError):
        return "Please enter a valid whole-number age."

    if age < MIN_AGE or age > MAX_AGE:
        return "This planner supports adults aged 19-59."

    return "Age accepted. You can continue!"


# ==========================================
# R1: EQUIPMENT CHECK
# ==========================================

def check_R1(plan, profile=None):

    if profile is None:
        profile = {}

    available_equipment = profile.get(
        "equipment",
        ALLOWED_EQUIPMENT
    )

    if isinstance(available_equipment, str):
        available_equipment = {available_equipment.lower()}

    available_equipment = {
        item.strip().lower()
        for item in available_equipment
        if isinstance(item, str)
    }

    for day in plan:

        for exercise in day.get("exercises", []):

            equipment = exercise.get("equipment")

            if not isinstance(equipment, str):
                return False

            equipment = equipment.strip().lower()

            if equipment not in ALLOWED_EQUIPMENT:
                return False

            if equipment not in available_equipment:
                return False

    return True


# ==========================================
# R2: DIFFICULTY CHECK
# ==========================================

def check_R2(plan, profile=None):

    if profile is None:
        profile = {}

    user_level = profile.get("level", "beginner")

    if not isinstance(user_level, str):
        return False

    user_level = user_level.strip().lower()

    if user_level not in LEVEL_RANK:
        return False

    user_level_rank = LEVEL_RANK[user_level]

    for day in plan:

        for exercise in day.get("exercises", []):

            level = exercise.get("level")

            if not isinstance(level, str):
                return False

            level = level.strip().lower()

            if level not in ALLOWED_LEVELS:
                return False

            exercise_level_rank = LEVEL_RANK[level]

            if exercise_level_rank > user_level_rank:
                return False

    return True


# ==========================================
# R3: SESSION TIME CHECK
# ==========================================

def check_R3(plan, profile=None):

    if profile is None:
        profile = {}

    session_limit = profile.get(
        "session_minutes",
        MAX_SESSION_MINUTES
    )

    try:
        session_limit = float(session_limit)
    except (ValueError, TypeError):
        return False

    if session_limit <= 0:
        return False

    for day in plan:

        total_time = 0

        for exercise in day.get("exercises", []):

            try:
                sets = float(exercise["sets"])
                minutes = float(exercise["minutes_per_set"])

                if sets <= 0 or minutes <= 0:
                    return False

                total_time += sets * minutes

            except (KeyError, ValueError, TypeError):
                return False

        if total_time > session_limit:
            return False

    return True


# ==========================================
# R4: RECOVERY CHECK
# ==========================================

def check_R4(plan, profile=None):

    days = {}

    for day in plan:

        day_index = day.get("day_index")

        if (
            not isinstance(day_index, int)
            or isinstance(day_index, bool)
            or day_index < 0
            or day_index > 6
        ):
            return False

        if day_index in days:
            return False

        muscles = set()

        for exercise in day.get("exercises", []):

            primary = exercise.get("primary_muscle")

            if not isinstance(primary, str):
                return False

            muscles.add(primary.strip().lower())

            secondary = exercise.get("secondary_muscles", [])

            if isinstance(secondary, str):
                secondary = secondary.replace(",", ";").split(";")

            for muscle in secondary:

                if isinstance(muscle, str) and muscle.strip():
                    muscles.add(muscle.strip().lower())

        days[day_index] = muscles

    # Check consecutive calendar days
    for day_index, muscles in days.items():

        next_day = day_index + 1

        if next_day in days:

            if muscles.intersection(days[next_day]):
                return False

    return True


# ==========================================
# R5: NO REPEATED EXERCISES
# ==========================================

def check_R5(plan, profile=None):

    # Check repetitions separately for each session

    for day in plan:

        used_exercises = set()

        for exercise in day.get("exercises", []):

            exercise_id = exercise.get(
                "id",
                exercise.get("exercise_id")
            )

            if exercise_id is None:
                return False

            if exercise_id in used_exercises:
                return False

            used_exercises.add(exercise_id)

    return True


# ==========================================
# R6: WEEKLY VOLUME CHECK
# ==========================================

def check_R6(
    plan,
    profile=None,
    weekly_set_limits=None
):

    if weekly_set_limits is None:
        weekly_set_limits = DEFAULT_WEEKLY_SET_LIMITS

    if not isinstance(weekly_set_limits, dict):
        return False

    if not MUSCLE_GROUPS.issubset(weekly_set_limits.keys()):
        return False

    weekly_sets = {
        muscle: 0
        for muscle in MUSCLE_GROUPS
    }

    for day in plan:

        for exercise in day.get("exercises", []):

            muscle = exercise.get("primary_muscle")

            if not isinstance(muscle, str):
                return False

            muscle = muscle.strip().lower()

            if muscle not in MUSCLE_GROUPS:
                return False

            try:
                sets = float(exercise["sets"])
            except (KeyError, ValueError, TypeError):
                return False

            if sets <= 0:
                return False

            weekly_sets[muscle] += sets

    for muscle in MUSCLE_GROUPS:

        limits = weekly_set_limits[muscle]

        if not isinstance(limits, dict):
            return False

        try:
            minimum = float(limits["min"])
            maximum = float(limits["max"])
        except (KeyError, ValueError, TypeError):
            return False

        if minimum < 0 or maximum < minimum:
            return False

        total = weekly_sets[muscle]

        if total < minimum or total > maximum:
            return False

    return True


# ==========================================
# CHECK ALL RULES
# ==========================================

def check_plan(plan, profile, weekly_set_limits=None):

    # Check age first

    if not check_R0(profile):

        return {
            "R0_Age_Eligibility": False,
            "Age_Message": get_age_message(
                profile.get("age")
            ),
            "R1_Equipment": None,
            "R2_Level": None,
            "R3_Time": None,
            "R4_Recovery": None,
            "R5_No_Repeats": None,
            "R6_Weekly_Volume": None,
            "All_Checked_Rules_Pass": False,
            "All_Rules_Pass": False
        }

    # Run all six exercise checks

    results = {
        "R0_Age_Eligibility": True,

        "R1_Equipment": check_R1(
            plan,
            profile
        ),

        "R2_Level": check_R2(
            plan,
            profile
        ),

        "R3_Time": check_R3(
            plan,
            profile
        ),

        "R4_Recovery": check_R4(
            plan,
            profile
        ),

        "R5_No_Repeats": check_R5(
            plan,
            profile
        ),

        "R6_Weekly_Volume": check_R6(
            plan,
            profile,
            weekly_set_limits
        )
    }

    results["All_Checked_Rules_Pass"] = all(
        value is True
        for value in results.values()
    )

    results["All_Rules_Pass"] = results[
        "All_Checked_Rules_Pass"
    ]

    return results
