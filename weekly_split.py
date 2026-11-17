
# --------------------------------------------------
# MUSCLE GROUPS
# --------------------------------------------------

MUSCLE_GROUPS = [
    "chest",
    "back",
    "shoulders",
    "biceps",
    "triceps",
    "quads",
    "hamstrings_glutes",
    "calves",
    "core"
]


# --------------------------------------------------
# DAY NAMES
# --------------------------------------------------

DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


# --------------------------------------------------
# DFS WEEKLY WORKOUT SPLIT
# --------------------------------------------------

def dfs_split(available_days, preferred_days):

    # Validate selected workout days

    if not isinstance(preferred_days, (list, tuple)):
        raise ValueError("Workout days must be provided as a list.")

    if not 1 <= len(preferred_days) <= 6:
        raise ValueError("Choose between 1 and 6 workout days.")

    if any(type(day) != int for day in preferred_days):
        raise ValueError("Invalid day selection.")

    if len(set(preferred_days)) != len(preferred_days):
        raise ValueError("You cannot select the same day twice.")

    if any(day not in range(6) for day in preferred_days):
        raise ValueError("Choose days from Monday to Saturday.")

    if available_days != len(preferred_days):
        raise ValueError("Number of workout days does not match selection.")

    # Sort selected workout days

    workout_days = sorted(preferred_days)

    available_days = len(workout_days)

    # Create an empty split

    split = {
        day: [] for day in workout_days
    }

    # Maximum number of muscle groups per day

    max_groups = (
        len(MUSCLE_GROUPS) + available_days - 1
    ) // available_days

    # --------------------------------------------------
    # RECOVERY CHECK
    # --------------------------------------------------

    def recovery_check(day, muscle):

        for neighbor in (day - 1, day + 1):

            if neighbor in split:

                if muscle in split[neighbor]:
                    return False

        return True

    # --------------------------------------------------
    # DFS WITH BACKTRACKING
    # --------------------------------------------------

    def search(index):

        # All muscle groups have been assigned

        if index == len(MUSCLE_GROUPS):

            # Every selected day must have a workout

            return all(
                split[day] for day in workout_days
            )

        muscle = MUSCLE_GROUPS[index]

        # Try days with fewer muscle groups first

        sorted_days = sorted(
            workout_days,
            key=lambda day: len(split[day])
        )

        for day in sorted_days:

            # Check maximum groups and recovery

            if (
                len(split[day]) < max_groups
                and recovery_check(day, muscle)
            ):

                split[day].append(muscle)

                if search(index + 1):
                    return True

                # Backtracking

                split[day].pop()

        return False

    # Generate weekly split

    if search(0):

        return split

    return None


# --------------------------------------------------
# TEST WEEKLY SPLIT
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== WEEKLY WORKOUT PLANNER ==========")

    print("\nAvailable gym days:")
    print("Monday, Tuesday, Wednesday, Thursday, Friday, Saturday")

    print("\nSunday: GYM CLOSED")

    day_numbers = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5
    }

    try:

        selected_names = input(
            "\nEnter your preferred gym days separated by commas: "
        )

        names = [
            name.strip().lower()
            for name in selected_names.split(",")
            if name.strip()
        ]

        if not names:
            raise ValueError("Please select at least one day.")

        invalid_days = [
            name for name in names
            if name not in day_numbers
        ]

        if invalid_days:
            raise ValueError(
                "Choose days from Monday to Saturday only."
            )

        if len(names) != len(set(names)):
            raise ValueError(
                "You cannot select the same day twice."
            )

        preferred_days = [
            day_numbers[name]
            for name in names
        ]

        available_days = len(preferred_days)

        result = dfs_split(
            available_days,
            preferred_days
        )

        if result:

            print("\nSelected workout days:", available_days)

            print("\n========== WEEKLY WORKOUT SCHEDULE ==========\n")

            for day in range(6):

                if day in result:
                    print(
                        DAY_NAMES[day],
                        ":",
                        result[day]
                    )

                else:
                    print(
                        DAY_NAMES[day],
                        ": REST DAY"
                    )

            print("\nSunday: GYM CLOSED")

        else:

            print("\nNo valid workout split found.")

    except ValueError as error:

        print("\nInput error:", error)
