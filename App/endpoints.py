import json
from dataclasses import dataclass

def get_base_url():
    with open("server.json") as json_file:
        data = json.load(json_file)
        return data["base_url"]

@dataclass
class Url:
    base = get_base_url()
    email_login = base+"/user/login/email"
    username_login = base+"/user/login/username"
    create_user = base+"/user/create/add"
    verify_user = base+"/user/create/verify"
    reset_password = base+"/user/login/forgot"
    update_account = base+"/user/update/details"
    update_password = base+"/user/update/password"
    get_user_details = base+"/user/details"
    logout = base+"/user/logout"
    


if __name__ == "__main__":
    print(get_base_url())