# This module is used to store the endpoints used to contact the server
import json


def get_base_url():  # Gets the base url from server.json
    with open("server.json") as json_file:
        data = json.load(json_file)
        return data["base_url"]


class Url:  # Stores the actual endpoints
    base = get_base_url()
    login = base+"/user/login"
    create_user = base+"/user/create/add"
    verify_user = base+"/user/create/verify"
    reset_password = base+"/user/login/forgot"
    update_account = base+"/user/update/details"
    update_password = base+"/user/update/password"
    get_user_details = base+"/user/details"
    logout = base+"/user/logout"

    get_exercises = base+"/exercises"
    add_workout_plan = base+"/workout/plan/add"
    workout_plan = base + "/workout-plan"
    workout = base + "/workout"
    workout_exercise = base + "/workout-exercise"

    workout_exercise_history = base + "/workout-exercise-history"
    set_history = base + "/set-history"
