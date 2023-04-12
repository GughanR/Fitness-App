import user
from endpoints import Url
import requests
import json
import string
from user import get_access_token, get_user_details


class WorkoutPlan:
    def __init__(self, data: dict = {}):
        # Given dictionary will be used to add attributes
        # If no dict given then default dict will be empty
        self.workout_plan_id = data.get("workout_plan_id")
        self.workout_plan_name = data.get("workout_plan_name")
        self.workout_plan_type = data.get("workout_plan_type")
        self.workout_plan_goal = data.get("workout_plan_goal")
        self.workout_list = data.get("workout_list", [])
        self.last_workout = data.get("last_workout")

    def save_new_plan(self):
        # Save new plan in database
        payload = convert_to_json(self)
        token = {
            "token": get_access_token()["token"]
        }
        url = Url.add_workout_plan

        response = requests.post(url=url, json=payload, params=token)

        return response


class Exercise:
    def __init__(self, data: dict = {}):
        # Given dictionary will be used to add attributes
        # If no dict given then default dict will be empty
        self.exercise_id = data.get("exercise_id")
        self.workout_exercise_id = data.get("workout_exercise_id")
        self.exercise_name = data.get("exercise_name")
        self.min_reps = data.get("min_reps")
        self.max_reps = data.get("max_reps")
        self.muscle_group = data.get("muscle_group")
        self.muscle_subgroup = data.get("muscle_subgroup")
        self.compound = data.get("compound")
        self.completed = data.get("completed")
        self.workout_exercise_number = data.get("workout_exercise_number")


class Workout:
    def __init__(self, data: dict = {}):
        # Given dictionary will be used to add attributes
        # If no dict given then default dict will be empty
        self.workout_id = data.get("workout_id")
        self.workout_number = data.get("workout_number")
        self.workout_name = data.get("workout_name")
        self.exercise_list = data.get("exercise_list", [])


class ExerciseHistory:
    def __init__(self, data: dict = {}):
        # Given dictionary will be used to add attributes
        # If no dict given then default dict will be empty
        self.weight_used = data.get("weight_used")
        self.unit_weight = data.get("unit_weight")
        self.reps_completed = data.get("reps_completed")
        self.set_number = data.get("set_number")
        self.date_completed = data.get("date_completed")


def convert_to_json(py_obj):
    json_data = {}
    for key, value in py_obj.__dict__.items():
        if type(value) == list:
            json_list = []
            for item in value:
                json_list.append(convert_to_json(item))
            json_data[key] = json_list

        else:
            json_data[key] = value
    return json_data


def convert_exercise(exercise_json):
    exercise_obj = Exercise(exercise_json)
    return exercise_obj


def convert_workout(workout_json):
    exercise_list = workout_json.get("exercise_list")
    exercise_obj_list = []
    # If exercise list exists then convert each exercise to object
    if exercise_list:
        for exercise in exercise_list:
            exercise_obj_list.append(convert_exercise(exercise))
        # Remove old list from dictionary
        del workout_json["exercise_list"]

    # Save details
    workout_obj = Workout(workout_json)
    # Save new workout list
    workout_obj.exercise_list = exercise_obj_list

    return workout_obj


def convert_workout_plan(workout_plan_json):
    workout_list = workout_plan_json.get("exercise_list")
    workout_obj_list = []
    # If exercise list exists then convert each exercise to object
    if workout_list:
        for workout in workout_list:
            workout_obj_list.append(convert_workout(workout))
        # Remove old list from dictionary
        del workout_plan_json["exercise_list"]

    # Save details
    workout_plan_obj = WorkoutPlan(workout_plan_json)
    # Save new workout list
    workout_plan_obj.workout_list = workout_obj_list

    return workout_plan_obj


def convert_exercise_history(exercise_history_list):
    obj_list = []
    for json_obj in exercise_history_list:
        obj_list.append(ExerciseHistory(json_obj))
    return obj_list


def check_plan_name(name):
    alphabet = list(string.ascii_letters)
    digits = "1234567890"
    digits = list(digits)
    email_valid_char = [
        "!", "#", "$", "%", "&", "'", " *", "+", "-", "@",
        "/", "=", "?", "^", "_", "`", "{", "|", "}", "~", "."
    ]
    contains_char = False
    for char in name:
        if char == " ":
            continue
        elif char not in (alphabet + digits + email_valid_char + ["(", ")"]):
            return "Invalid character(s) in plan name"
        else:
            contains_char = True

    if not contains_char:
        return "A plan name must be entered"

    return True


def get_exercises():
    token = {
        "token": get_access_token()["token"]
    }
    response = requests.get(url=Url.get_exercises, params=token)

    return response


def check_plan_type(plan_type, muscles_chosen):
    # Set muscle groups
    push_muscles = ["chest", "triceps", "shoulders"]
    pull_muscles = ["back", "biceps", "forearms"]
    leg_muscles = ["quadriceps", "hamstrings", "calves"]

    if plan_type == "push pull legs":
        muscle_groups = [push_muscles, pull_muscles, leg_muscles]
    elif plan_type == "upper lower":
        muscle_groups = [push_muscles + pull_muscles, leg_muscles]
    else:
        muscle_groups = [push_muscles + pull_muscles + leg_muscles]

    # Check that at least one muscle from each group is in chosen muscles
    all_valid = True
    for muscle_group in muscle_groups:
        group_valid = False
        for muscle in muscle_group:
            if muscle in muscles_chosen:
                group_valid = True
        if not group_valid:
            all_valid = False

    return all_valid


def check_num_of_days(plan_type, num_of_days):
    if plan_type == "push pull legs":
        minimum_days = 3
    elif plan_type == "upper lower":
        minimum_days = 2
    else:
        minimum_days = 1

    if num_of_days < minimum_days:
        return [False, minimum_days]
    else:
        return [True]


def load_exercises(json_data_list):
    exercises_list = []
    for json_data in json_data_list:
        exercise = Exercise(json_data)
        exercises_list.append(exercise)
    return exercises_list


def get_muscles(exercises):
    # Returns dictionary containing muscles and their subgroups
    muscles_dict = {}
    for exercise in exercises:
        # If muscle group not in dict then create a new subgroup queue (list)
        if not muscles_dict.get(exercise.muscle_group):
            muscles_dict[exercise.muscle_group] = []

        # Append muscle subgroup to corresponding list
        if exercise.muscle_subgroup not in muscles_dict[exercise.muscle_group]:
            muscles_dict[exercise.muscle_group].append(exercise.muscle_subgroup)

        # Append exercise to

    return muscles_dict


def get_exercises_for_subgroup(exercises, subgroup):
    return [exercise for exercise in exercises if exercise.muscle_subgroup == subgroup]


def create_workout_plan(plan_goal, muscles_chosen, plan_type, plan_name, num_of_days):
    # Get exercises
    response = get_exercises()
    exercises_json = json.loads(response.content.decode("utf-8"))
    exercises = load_exercises(exercises_json)

    # Set muscle groups
    push_muscles = ["chest", "triceps", "shoulders"]
    pull_muscles = ["back", "biceps", "forearms"]
    leg_muscles = ["quadriceps", "hamstrings", "calves"]

    if plan_type == "push pull legs":
        exercise_muscles = [push_muscles, pull_muscles, leg_muscles]
    elif plan_type == "upper lower":
        exercise_muscles = [push_muscles + pull_muscles, leg_muscles]
    else:
        exercise_muscles = [push_muscles + pull_muscles + leg_muscles]

    # Filter muscle groups
    filtered_exercise_muscles = []
    for muscle_group in exercise_muscles:
        filtered_muscle_group = []
        for muscle in muscle_group:
            if muscle in muscles_chosen:
                filtered_muscle_group.append(muscle)
        filtered_exercise_muscles.append(filtered_muscle_group)

    # Create queues
    muscle_subgroups_dict = get_muscles(exercises)
    muscle_group_exercises = {}
    for muscle_group in push_muscles + pull_muscles + leg_muscles:
        muscle_subgroup_queue = []
        for muscle_subgroup in muscle_subgroups_dict[muscle_group]:
            exercise_queue = get_exercises_for_subgroup(exercises, muscle_subgroup)
            muscle_subgroup_queue.append(exercise_queue)
        muscle_group_exercises[muscle_group] = muscle_subgroup_queue

    # Create each workout
    workout_plan = WorkoutPlan()
    for day_no in range(num_of_days):
        workout = Workout()
        n = day_no % len(filtered_exercise_muscles)
        potential_muscles = filtered_exercise_muscles[n]
        selected_exercises = []

        for muscle_group in potential_muscles:
            muscle_subgroup_queue = muscle_group_exercises[muscle_group]
            # Add two exercises per muscle group
            for i in range(2):
                # Dequeue
                exercise_queue = muscle_subgroup_queue.pop(0)
                exercise = exercise_queue.pop(0)
                # Only add exercise if it is not already there
                if exercise not in selected_exercises:  # TODO: ERROR fixed
                    selected_exercises.append(exercise)
                # Enqueue again
                exercise_queue.append(exercise)
                muscle_subgroup_queue.append(exercise_queue)

            # Sort exercises
            for i, exercise in enumerate(selected_exercises):
                if exercise.compound:
                    # Move exercise to front
                    selected_exercises.insert(0, selected_exercises.pop(i))

            # Set number of each exercise
            for i, exercise in enumerate(selected_exercises):
                exercise.workout_exercise_number = i

        # Save workout object details
        workout.workout_number = day_no
        workout.workout_name = f"Workout {day_no}"
        workout.exercise_list = selected_exercises
        # Append workout object to workout_plan object's list
        workout_plan.workout_list.append(workout)

    # Save workout plan object details
    workout_plan.workout_plan_goal = str(plan_goal).lower()
    workout_plan.workout_plan_name = str(plan_name)
    workout_plan.workout_plan_type = str(plan_type).lower()

    return workout_plan


def save_new_plan(new_plan):
    # Save new plan in database
    payload = convert_to_json(new_plan)
    token = {
        "token": get_access_token()["token"]
    }
    url = Url.add_workout_plan

    response = requests.post(url=url, json=payload, params=token)

    return response


def get_workout_plans():
    token = {
        "token": get_access_token()["token"]
    }
    response = requests.get(url=Url.workout_plan, params=token)

    return response


def get_workouts_in_plan(plan_id):
    params = {
        "token": get_access_token()["token"],
        "workout_plan_id": plan_id
    }
    response = requests.get(url=Url.workout, params=params)

    return response


def get_exercises_in_workout(workout_id):
    params = {
        "token": get_access_token()["token"],
        "workout_id": workout_id
    }
    response = requests.get(url=Url.workout_exercise, params=params)

    return response


def update_workout_plan(updated_plan):
    params = {
        "token": get_access_token()["token"]
    }
    payload = convert_to_json(updated_plan)
    response = requests.put(url=Url.workout_plan, params=params, json=payload)

    return response


def update_workout(updated_workout):
    params = {
        "token": get_access_token()["token"]
    }
    payload = convert_to_json(updated_workout)
    response = requests.put(url=Url.workout, params=params, json=payload)

    return response


def delete_workout_plan(plan_to_delete):
    params = {
        "token": get_access_token()["token"]
    }
    payload = convert_to_json(plan_to_delete)
    response = requests.delete(url=Url.workout_plan, params=params, json=payload)

    return response


def delete_exercise(exercise_to_delete):
    params = {
        "token": get_access_token()["token"]
    }
    payload = convert_to_json(exercise_to_delete)
    response = requests.delete(url=Url.workout_exercise, params=params, json=payload)

    return response


def delete_workout(workout_to_delete):
    params = {
        "token": get_access_token()["token"]
    }
    payload = convert_to_json(workout_to_delete)
    response = requests.delete(url=Url.workout, params=params, json=payload)

    return response


def add_workout(new_workout, workout_plan_id):
    # Save new plan in database
    payload = convert_to_json(new_workout)
    params = {
        "token": get_access_token()["token"],
        "workout_plan_id": workout_plan_id
    }
    url = Url.workout

    response = requests.post(url=url, json=payload, params=params)

    return response


def add_workout_exercise(new_workout_exercise, workout_id):
    # Save new plan in database
    params = {
        "token": get_access_token()["token"],
        "workout_id": workout_id,
        "exercise_id": new_workout_exercise.exercise_id,
        "num": new_workout_exercise.workout_exercise_number
    }
    url = Url.workout_exercise

    response = requests.post(url=url, params=params)

    return response


def check_weight_input(weight):
    try:
        weight = float(weight)
        return (weight > 0) and (weight <= 1000)
    except:
        return False


def check_reps_input(reps):
    try:
        reps = int(reps)
        return (reps > 0) and (reps <= 150)
    except:
        return False


def add_workout_exercise_history(workout_exercise_id):
    # Save in database
    params = {
        "token": get_access_token()["token"],
        "workout_exercise_id": workout_exercise_id
    }
    url = Url.workout_exercise_history

    response = requests.post(url=url, params=params)

    return response


def add_set_history(exercise_history_id, set_number, reps_completed, weight_used, unit_weight):
    # Save in database
    params = {
        "token": get_access_token()["token"],
        "exercise_history_id": exercise_history_id,
        "set_number": set_number,
        "reps_completed": reps_completed,
        "weight_used": weight_used,
        "unit_weight": unit_weight
    }
    url = Url.set_history

    response = requests.post(url=url, params=params)

    return response


def get_exercise_history(exercise_id):
    params = {
        "token": get_access_token()["token"],
        "exercise_id": exercise_id
    }
    url = Url.set_history

    response = requests.get(url=url, params=params)

    return response


def exercise_reps(exercise, goal):
    average = (exercise.min_reps + exercise.max_reps) / 2
    if goal == "strength":
        min_reps = exercise.min_reps
        max_reps = int(average)
    elif goal == "size":
        min_reps = int(average)
        max_reps = exercise.max_reps
    else:
        min_reps = exercise.min_reps
        max_reps = exercise.max_reps
    return min_reps, max_reps


def linear_regression(x_values, y_values, given_x):
    try:
        # Get data required
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = 0
        sum_x2 = 0
        for i in range(len(x_values)):
            sum_xy += x_values[i] * y_values[i]
            sum_x2 += x_values[i] ** 2
        n = len(x_values)

        # Regression coefficient
        S_xy = sum_xy - (sum_x * sum_y) / n
        S_xx = sum_x2 - (sum_x ** 2) / n
        b = S_xy / S_xx

        # Get a
        a = (sum_y / n) - (sum_x / n) * b

        # Estimate
        y_est = a + given_x * b
    except ZeroDivisionError:
        y_est = 0

    return y_est


def calculate_weight(exercise, exercise_history, current_set, last_set, goal):
    # Calculate min and max reps for exercise
    min_reps, max_reps = exercise_reps(exercise, goal)

    if current_set == 1:
        # Convert to kg
        for e in exercise_history:
            if e.unit_weight != "KG":
                e.weight_used = e.weight_used/2.205

        # Calculate data
        first_set_history = [e for e in exercise_history if e.set_number == 1]
        workout_nums = [x for x in range(1, len(first_set_history)+1)]
        weight_history = [e.weight_used for e in first_set_history]

        # Use regression for new weight
        new_weight = linear_regression(workout_nums, weight_history, len(workout_nums)+1)

        # Get weight used in first set of last workout
        last_weight_used = first_set_history[-1].weight_used
        # Get last reps performed in first set of last workout
        last_reps_performed = first_set_history[-1].reps_completed

        # Check that user will perform more than before
        if new_weight <= last_weight_used:
            if last_reps_performed >= max_reps:
                new_weight = last_weight_used + 2
            else:
                new_weight = last_weight_used
    else:
        # If set is not the first
        new_weight = last_set.weight_used
        last_reps_performed = last_set.reps_completed
        # Edit weight based on last performance
        if last_reps_performed >= max_reps:
            new_weight += 2
        elif last_reps_performed < min_reps:
            new_weight -= 2

    return new_weight


def calculate_reps(exercise, exercise_history, current_set, weight, last_set, goal):
    # Get rep ranges
    min_reps, max_reps = exercise_reps(exercise, goal)

    if current_set == 1:
        # Convert to kg
        for e in exercise_history:
            if e.unit_weight != "KG":
                e.weight_used = e.weight_used / 2.205

        # Calculate data
        first_set_history = [e for e in exercise_history if e.set_number == 1]
        exercise_history_for_weight = [e for e in first_set_history if e.weight_used == weight]
        workout_nums = [x for x in range(1, len(exercise_history_for_weight) + 1)]
        rep_history_for_weight = [e.reps_completed for e in exercise_history_for_weight]

        # Check if user has done weight before
        if len(exercise_history_for_weight) == 0:
            return min_reps

        # Use regression for reps
        new_reps = int(linear_regression(workout_nums, rep_history_for_weight, len(workout_nums)+1))

        # Check that user does more than last time
        last_reps_performed = rep_history_for_weight[-1]
        if new_reps <= last_reps_performed:
            new_reps = last_reps_performed + 1
    else:
        # Keeps reps same from last set
        new_reps = last_set.reps_completed

    return new_reps


if __name__ == "__main__":
    response = get_exercise_history(31)
    l = json.loads(response.content.decode("utf-8"))
    l = convert_exercise_history(l)
    e = Exercise()
    e.min_reps = 2
    e.max_reps = 10
    h = ExerciseHistory()
    h.reps_completed=9
    h.weight_used=20

    print(calculate_weight(e, l, 1, h, "size"))
    print(calculate_reps(e, l, 2, 5, h, "size"))


    linear_regression(
        [1, 2, 5, 7, 8, 9, 10],
        [7, 9, 13, 15, 14, 17, 20],
        2
    )
