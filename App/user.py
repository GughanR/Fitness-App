# This module is reponsible for allowing access to users
import string
import requests
import json
from endpoints import Url
from datetime import datetime

def check_name(name):
    alphabet = list(string.ascii_letters)
    for char in name:
        if char not in alphabet:
            if ((char != " ") and (char != "'")):
                return "Name must only contain alphabetical characters"
    return True

def check_email(email):
    alphabet = list(string.ascii_letters)
    digits = "1234567890"
    digits = list(digits)
    email_valid_char = [
        "!", "#", "$", "%", "&", "'"," *", "+", "-", "@",
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

#########################################################
def check_valid_details(name, email, username, password):
    alphabet = list(string.ascii_letters)
    for char in name:
        if char not in alphabet:
            if ((char != " ") and (char != "'")):
                return {""}
    
    digits = "1234567890"
    digits = list(digits)
    email_valid_char = [
        "!", "#", "$", "%", "&", "'"," *", "+", "-", 
        "/", "=", "?", "^", "_", "`", "{", "|", "}", "~"
        ]
    for char in email:
        if char in (alphabet + digits + email_valid_char):
            return False
    num_of_ats = email.count("@")    
    num_of_dots = email.count(".")
    if num_of_ats != 1 or num_of_dots == 0:
        return False
    
    for char in username:
        if char not in alphabet:
            return False
    
    if len(password) < 8:
        return False
    contains_number = False
    for digit in digits:
        if digit in password:
            contains_number = True
    if contains_number == False:
        return False
#########################################################

def is_email(user_input):
    if "@" in user_input:
        return True
    else:
        return False

def get_access_token():
    with open("access_token.json") as json_file:
        data = json.load(json_file)
        return data

def login(user_input, password):
    payload = {
        "password": password
    }

    if is_email(user_input) == True:
        login_url = Url.email_login
        payload["email_address"] = user_input
    else:
        login_url = Url.username_login
        payload["username"] = user_input

    
    response = requests.get(url=login_url, params=payload)
    response_str = response.content.decode("utf-8") # decode bytestring and convert to json
    access_token = json.dumps(json.loads(response_str), indent=4)

    with open("access_token.json", "w+") as json_file:
        json_file.write(access_token)

    return response
    
def create_account(full_name, email_address, user_name,  password):
    payload = {
        "full_name": full_name,
        "email_address": email_address,
        "user_name": user_name,
        "password": password
    }
    url = Url.create_user

    response = requests.post(url=url, json=payload)

    return response

def verify(full_name, email_address, user_name,  password, verification_code):
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
    expiry_time = token["expiry_time"].replace("T", " ")
    expiry_time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")

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

    response = requests.put(url=url, params=get_access_token(), json=payload)
    
    return response

def get_user_details():
    payload = {
        "token": get_access_token()["token"]
    }
    url = Url.get_user_details

    response = requests.get(url=url, params=payload)
    
    return json.loads(response.content.decode("utf-8"))
    

if __name__ == "__main__":
    print(get_user_details())