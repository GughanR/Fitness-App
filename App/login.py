# This module is reponsible for allowing access to users
import string
import requests
import json
from endpoints import Url

def check_valid_details(name, email, username, password):
    alphabet = list(string.ascii_letters)
    
    for char in name:
        if char not in alphabet:
            if ((char != " ") and (char != "'")):
                return False
    
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
    if check_valid_details(full_name, email_address, user_name, password):
        pass
    else:
        return False
    payload = {
        "full_name": full_name,
        "email_address": email_address,
        "user_name": user_name,
        "password": password
    }
    url = Url.create_user

    response = requests.post(url=url, json=payload)

    return response
    

if __name__ == "__main__":
    login("string", "string")