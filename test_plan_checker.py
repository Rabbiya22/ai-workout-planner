from plan_checker import check_plan, check_R0


# ==========================================
# SAMPLE PROFILE
# ==========================================

profile = {
    "age": 25
}


# ==========================================
# SAMPLE PLAN
# Three workout days, nine muscle groups
# ==========================================

def make_plan():

    muscle_groups = [
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

    plan = []

    exercise_number = 1

    for day_index in [0, 2, 4]:

        exercises = []

        for muscle in muscle_groups[
            (day_index // 2) * 3:
            (day_index // 2) * 3 + 3
        ]:

            exercises.append({
                "id": f"E{exercise_number}",
                "name": f"Exercise {exercise_number}",
                "equipment": "bodyweight",
                "level": "beginner",
                "primary_muscle": muscle,
                "secondary_muscles": [],
                "sets": 3,
                "minutes_per_set": 3
            })

            exercise_number += 1

        plan.append({
            "day_index": day_index,
            "exercises": exercises
        })

    return plan


# ==========================================
# TEST 1: ALL RULES PASS
# ==========================================

print("\n========== TEST 1: CORRECT PLAN ==========")

plan = make_plan()

results = check_plan(plan, profile)

for rule, result in results.items():
    print(rule, ":", result)


assert results["R0_Age_Eligibility"] is True
assert results["R1_Equipment"] is True
assert results["R2_Level"] is True
assert results["R3_Time"] is True
assert results["R4_Recovery"] is True
assert results["R5_No_Repeats"] is True
assert results["R6_Weekly_Volume"] is True
assert results["All_Rules_Pass"] is True


# ==========================================
# TEST 2: R1 EQUIPMENT FAIL
# ==========================================

print("\n========== TEST 2: R1 EQUIPMENT ==========")

plan = make_plan()
plan[0]["exercises"][0]["equipment"] = "unknown"

result = check_plan(plan, profile)

print("R1:", result["R1_Equipment"])
assert result["R1_Equipment"] is False


# ==========================================
# TEST 3: R2 DIFFICULTY FAIL
# ==========================================

print("\n========== TEST 3: R2 DIFFICULTY ==========")

plan = make_plan()
plan[0]["exercises"][0]["level"] = "expert"

result = check_plan(plan, profile)

print("R2:", result["R2_Level"])
assert result["R2_Level"] is False


# ==========================================
# TEST 4: R3 TIME FAIL
# ==========================================

print("\n========== TEST 4: R3 SESSION TIME ==========")

plan = make_plan()

for exercise in plan[0]["exercises"]:
    exercise["minutes_per_set"] = 20

result = check_plan(plan, profile)

print("R3:", result["R3_Time"])
assert result["R3_Time"] is False


# ==========================================
# TEST 5: R4 RECOVERY FAIL
# ==========================================

print("\n========== TEST 5: R4 RECOVERY ==========")

plan = make_plan()

plan.insert(1, {
    "day_index": 1,
    "exercises": [{
        "id": "E10",
        "name": "Extra Chest Exercise",
        "equipment": "bodyweight",
        "level": "beginner",
        "primary_muscle": "chest",
        "secondary_muscles": [],
        "sets": 2,
        "minutes_per_set": 3
    }]
})

result = check_plan(plan, profile)

print("R4:", result["R4_Recovery"])
assert result["R4_Recovery"] is False


# ==========================================
# TEST 6: R5 REPEATED EXERCISE FAIL
# ==========================================

print("\n========== TEST 6: R5 NO REPEATS ==========")

plan = make_plan()

repeated = plan[0]["exercises"][0].copy()

plan[1]["exercises"].append(repeated)

result = check_plan(plan, profile)

print("R5:", result["R5_No_Repeats"])
assert result["R5_No_Repeats"] is False


# ==========================================
# TEST 7: R6 WEEKLY VOLUME FAIL
# ==========================================

print("\n========== TEST 7: R6 WEEKLY VOLUME ==========")

plan = make_plan()

# Chest has 3 sets in the correct plan.
# Change it to 7 sets, exceeding the maximum of 6.
plan[0]["exercises"][0]["sets"] = 7

result = check_plan(plan, profile)

print("R6:", result["R6_Weekly_Volume"])
assert result["R6_Weekly_Volume"] is False


# ==========================================
# TEST 8: R0 AGE FAIL
# ==========================================

print("\n========== TEST 8: R0 AGE ==========")

assert check_R0({"age": 16}) is False
assert check_R0({"age": 25}) is True
assert check_R0({"age": 65}) is False

print("R0 age tests passed!")


# ==========================================
# FINAL RESULT
# ==========================================

print("\n===================================")
print("ALL RULE TESTS COMPLETED SUCCESSFULLY")
print("R0, R1, R2, R3, R4, R5, R6")
print("===================================")