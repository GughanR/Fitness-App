# This module is responsible for managing requests related to account details and checking these details
import os
import string
import requests
import json
from endpoints import Url
from datetime import datetime
from set_cache_directory import CACHE_DIR


def check_name(name):
    alphabet = list(string.ascii_letters)
    for char in name:
        if char not in alphabet:
            if (char != " ") and (char != "'"):
                return "Name must only contain alphabetical characters"
    return True


def check_email(email):
    alphabet = list(string.ascii_letters)
    digits = "1234567890"
    digits = list(digits)
    email_valid_char = [
        "!", "#", "$", "%", "&", "'", " *", "+", "-", "@",
        "/", "=", "?", "^", "_", "`", "{", "|", "}", "~", "."
    ]
    for char in email:
        if char not in (alphabet + digits + email_valid_char):
            return "Invalid character(s)"
    num_of_ats = email.count("@")
    num_of_dots = email.count(".")
    if num_of_ats != 1 or num_of_dots == 0:
        return "Email must only contain one '@' and at least one '.'"
    return True


def check_username(username):
    alphabet = list(string.ascii_letters)
    for char in username:
        if char not in alphabet:
            return "Username must only contain alphabetical characters"
    return True


def check_password(password):
    digits = "1234567890"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    contains_number = False
    for digit in digits:
        if digit in password:
            contains_number = True
    if contains_number == False:
        return "Password must contain a number"
    return True


def get_access_token():
    with open(os.path.join(CACHE_DIR, "access_token.json")) as json_file:
        try:
            data = json.load(json_file)
        except:
            data = None
        return data


def login(username, password):
    payload = {
        "username": username,
        "password": password
    }
    login_url = Url.login

    response = requests.get(url=login_url, params=payload)
    response_str = response.content.decode("utf-8")  # decode bytestring and convert to json
    access_token = json.dumps(json.loads(response_str), indent=4)
    if response.status_code == 200:
        with open(os.path.join(CACHE_DIR, "access_token.json"), "w+") as json_file:
            json_file.write(access_token)

    return response


def create_account(full_name, email_address, user_name, password):
    payload = {
        "full_name": full_name,
        "email_address": email_address,
        "user_name": user_name,
        "password": password
    }
    url = Url.create_user

    response = requests.post(url=url, json=payload)

    return response


def verify(full_name, email_address, user_name, password, verification_code):
    payload = {
        "full_name": full_name,
        "email_address": email_address,
        "user_name": user_name,
        "password": password
    }
    code = {
        "verification_code": verification_code
    }
    url = Url.verify_user

    response = requests.post(url=url, params=code, json=payload)

    return response


def reset_password(email_address):
    payload = {
        "email_address": email_address
    }
    url = Url.reset_password

    response = requests.post(url=url, params=payload)

    return response


def check_access_token():
    # Check if token is valid
    token = get_access_token()
    current_time = datetime.now()
    try:
        expiry_time = token["expiry_time"].replace("T", " ")
        expiry_time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")
    except:
        return False

    if current_time < expiry_time:
        return True
    else:
        return False


def update_account(full_name, email_address, user_name):
    payload = {
        "full_name": full_name,
        "email_address": email_address,
        "user_name": user_name
    }
    url = Url.update_account
    token = {
        "token": get_access_token()["token"]
    }

    response = requests.put(url=url, params=token, json=payload)

    return response


def update_password(old_pw, new_pw):
    payload = {
        "old_password": old_pw,
        "new_password": new_pw,
        "token": get_access_token()["token"]
    }
    url = Url.update_password

    response = requests.put(url=url, params=payload)

    return response


def update_weight_unit(weight_unit):
    payload = {
        "unit_weight": weight_unit
    }
    url = Url.update_account
    token = {
        "token": get_access_token()["token"]
    }

    response = requests.put(url=url, params=token, json=payload)

    return response


def get_user_details():
    payload = {
        "token": get_access_token()["token"]
    }
    url = Url.get_user_details

    response = requests.get(url=url, params=payload)

    return json.loads(response.content.decode("utf-8"))


def logout():
    payload = {
        "token": get_access_token()["token"]
    }
    url = Url.logout

    response = requests.put(url=url, params=payload)

    if response.status_code == 200 or 403:
        # Delete contents of access_token
        with open(os.path.join(CACHE_DIR, "access_token.json"), "w+") as json_file:
            pass

    return response


if __name__ == "__main__":
    print(get_user_details())
