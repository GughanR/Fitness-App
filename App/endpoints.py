import json

def get_base_url():
    with open("server.json") as json_file:
        data = json.load(json_file)
        return data["base_url"]


class Url:
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
    


if __name__ == "__main__":
    print(get_base_url())