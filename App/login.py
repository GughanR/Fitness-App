# This module is reponsible for allowing access to users
import string

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



if __name__ == "__main__":
    print(check_valid_details(" ", ">@.", "c", "dddddddd0"))