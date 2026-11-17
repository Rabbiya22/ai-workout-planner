
import csv
from pathlib import Path


def filter_exercises(exercises, profile):

    # Filter exercises according to experience level only
    levels = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    user_level = levels.get(
        profile["level"].strip().lower(),
        0
    )

    if user_level == 0:
        return []

    filtered = []

    for exercise in exercises:

        difficulty = levels.get(
            exercise["level"].strip().lower(),
            0
        )

        if difficulty == 0 or difficulty > user_level:
            continue

        filtered.append(exercise)

    return filtered


def load_exercises():

    file_path = Path(__file__).parent / "exercises_v1.csv"

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        return list(reader)


if __name__ == "__main__":

    profile = {
        "level": "beginner"
    }

    exercises = load_exercises()

    filtered = filter_exercises(exercises, profile)

    print("\n========== EXERCISE FILTER TEST ==========")

    print("Total exercises:", len(exercises))
    print("Suitable exercises:", len(filtered))

    for exercise in filtered:

        print(
            exercise["name"],
            "| Level:", exercise["level"],
            "| Muscle:", exercise["primary_muscle"]
        )
