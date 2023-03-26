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
        self.workout_exercise_id = data.get("exercise_id")
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


def convert_to_json(py_obj):  # TODO: Document this algorithm
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
        elif char not in (alphabet + digits + email_valid_char):
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


def get_workout_plans():
    token = {
        "token": get_access_token()["token"]
    }
    response = requests.get(url=Url.get_workout_plan, params=token)

    return response


def get_workouts_in_plan(plan_id):
    params = {
        "token": get_access_token()["token"],
        "workout_plan_id": plan_id
    }
    response = requests.get(url=Url.get_workouts, params=params)

    return response


def get_exercises_in_workout(workout_id):
    params = {
        "token": get_access_token()["token"],
        "workout_id": workout_id
    }
    response = requests.get(url=Url.get_workout_exercises, params=params)

    return response

if __name__ == "__main__":
    print(create_workout_plan(1,
                        ["chest", "triceps", "shoulders", "back", "forearms", "quadriceps", "hamstrings", "calves"],
                        "push pull legs",
                        1,
                        3))
