# உ
import kivy

from kivy.app import App
from kivy.resources import resource_find
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.widget import Widget, WidgetBase
import time
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition, CardTransition
from kivy.uix.button import Button
from kivy.graphics import *
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.bottomnavigation.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivy.utils import get_color_from_hex 


import user
import json

Builder.load_file("My.kv")  # Load kivy file into main.py


def show_dialog(self, text):
    self.dialog = MDDialog(
        text=text
    )
    self.dialog.open()

class Background(FloatLayout):
    pass


class InitialScreenDecoration(FloatLayout):
    pass


class InitialScreen(Screen):
    pass


class LoginScreen(Screen):
    loginBtn = ObjectProperty(None)
    backBtn = ObjectProperty(None)
    unInput = ObjectProperty(None)
    pwInput = ObjectProperty(None)
    dialog = None

    def login(self):
        #
        #self.manager.current = "main"
        #
        empty = False
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                if len(widget_object.text) == 0:
                    empty = True
                    widget_object.helper_text = widget_object.hint_text + " must not be empty"
        if not empty:
            try:
                response = user.login(self.unInput.text, self.pwInput.text)

                if response.status_code != 200:
                    show_dialog(
                        self,
                        text=json.loads(response.content.decode("utf-8"))["detail"]
                    ) 
                else:
                    print("logged in")
                    # Pass user details to AccountPage
                    try:
                        user_details = user.get_user_details()
                        AccountPage.user_details = user_details
                    except Exception as e:
                        print(e)
                    # Change screen
                    self.manager.current = "main"

            except Exception as e:
                show_dialog(
                    self,
                    text=str(e)
                ) 

        

    def reset_inputs(self):
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                widget_object.text = ""
                widget_object.helper_text = ""


class ForgotPasswordScreen(Screen):

    def reset_inputs(self):
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                widget_object.text = ""
                widget_object.helper_text = ""

    def reset_password(self, email_address):
        try:
            response = user.reset_password(email_address)
            if response.status_code != 200:
                show_dialog(
                    self,
                    text=json.loads(response.content.decode("utf-8"))["detail"]
                ) 
            else:
                show_dialog(
                    self,
                    text="Password has been reset\n\nCheck your email"
                ) 
        except Exception as e:
            show_dialog(
                self, 
                text=str(e)
            )
            

class SignUpScreen(Screen):
    createAccountBtn = ObjectProperty(None)
    nameInput = ObjectProperty(None)
    emailInput = ObjectProperty(None)
    unInput = ObjectProperty(None)
    pwInput = ObjectProperty(None)
    dialog = None
    #verifyDialog = ObjectProperty(None)
    #codeInput = ObjectProperty(None)

    def create_account(self):
        invalid = False

        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:

                if "name" in widget_name:
                    response = user.check_name(widget_object.text)
                elif "email" in widget_name:
                    response = user.check_email(widget_object.text)
                elif "un" in widget_name:
                    response = user.check_username(widget_object.text)
                elif "pw" in widget_name:
                    response = user.check_password(widget_object.text)
                else:
                    response = True

                if len(widget_object.text) == 0:
                    invalid = True
                    widget_object.helper_text = widget_object.hint_text+" must not be empty"
                elif type(response) == str:
                    widget_object.helper_text = response
                    invalid = True
                else:
                    widget_object.helper_text = ""

        if not invalid:
            try:
                response = user.create_account(
                    self.nameInput.text,
                    self.emailInput.text,
                    self.unInput.text,
                    self.pwInput.text
                    )

                if response.status_code != 200:
                    show_dialog(
                        self,
                        text="Server error"
                    )
                else:
                    # Pass variables to verification screen
                    self.manager.screens[4].fullname = self.nameInput.text
                    self.manager.screens[4].email = self.emailInput.text
                    self.manager.screens[4].username = self.unInput.text
                    self.manager.screens[4].password = self.pwInput.text
                    self.manager.transition.direction = "left"
                    self.manager.current = "verify"

            except:
                show_dialog(
                    self,
                    text="Connection failed"
                )
            

    def reset_inputs(self):
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                widget_object.text = ""
                widget_object.helper_text = ""


class VerifyUserScreen(Screen):

    codeInput = ObjectProperty(None)
    fullname = None
    email = None
    username = None
    password = None
    dialog = None
    
    def reset_inputs(self):
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                widget_object.text = ""
                widget_object.helper_text = ""

    def verify(self):
        self.codeInput.helper_text = ""
        try:
            response = user.verify(
                full_name=self.fullname,
                email_address=self.email,
                user_name=self.username,
                password=self.password,
                verification_code=int(self.codeInput.text)
            )
            if response.status_code != 200:
                show_dialog(
                    self,
                    text=json.loads(response.content.decode("utf-8"))["detail"]
                ) 
                
            else:
                show_dialog(
                    self,
                    text="Account created\n\nPlease login"
                ) 
                
                self.manager.transition.direction = "left"
                self.manager.current = "login"

        except ValueError:
            self.codeInput.helper_text = "Verification code must be a number"

        except Exception as e:
            print(e)
            show_dialog(
                self,
                text="Connection failed"
            ) 
            


class MainScreen(Screen):
    pass

class AccountPage(MDScrollView):
    updateBtn = ObjectProperty(None)
    nameInput = ObjectProperty(None)
    emailInput = ObjectProperty(None)
    unInput = ObjectProperty(None)
    #pwInput = ObjectProperty(None)
    dialog = None
    #verifyDialog = ObjectProperty(None)
    #codeInput = ObjectProperty(None)
    user_details = None

    # Set values for current details (runs if user just logged in)
    if user_details:
        try:
            nameText = user_details["full_name"]
            emailText = user_details["email_address"]
            unText = user_details["user_name"]
        except Exception as e:
            print(e)

    # Set values for current details (runs when user already logged in)
    try:
        user_details = user.get_user_details()
        nameText = user_details["full_name"]
        emailText = user_details["email_address"]
        unText = user_details["user_name"]
    except:
        nameText = ""
        emailText = ""
        unText = ""  

    def refresh(self):  # Ran when screen is refreshed
        try:
            user_details = user.get_user_details()
            self.nameInput.text = user_details["full_name"]
            self.emailInput.text = user_details["email_address"]
            self.unInput.text = user_details["user_name"]
        except Exception as e:
            print(e)
            show_dialog(self, "Connection failed")

    def show(self):
        show_dialog(self, "con")

    def update_account(self):
        invalid = False

        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:

                if "name" in widget_name:
                    response = user.check_name(widget_object.text)
                elif "email" in widget_name:
                    response = user.check_email(widget_object.text)
                elif "un" in widget_name:
                    response = user.check_username(widget_object.text)
                else:
                    response = True

                if len(widget_object.text) == 0:
                    invalid = True
                    widget_object.helper_text = widget_object.hint_text+" must not be empty"
                elif type(response) == str:
                    widget_object.helper_text = response
                    invalid = True
                else:
                    widget_object.helper_text = ""

        if not invalid:
            try:
                response = user.update_account(
                    self.nameInput.text,
                    self.emailInput.text,
                    self.unInput.text
                    )

                if response.status_code != 200:
                    show_dialog(
                        self,
                        text=json.loads(response.content.decode("utf-8"))["detail"]
                    )
                    
                else:
                    show_dialog(
                        self,
                        text="Successfully updated"
                    )
                    

            except:
                show_dialog(
                    self,
                    text="Connection failed"
                ) 
                

class ChangePasswordScreen(Screen):
    pass

class FitnessApp(MDApp):
    x = 500
    Window.size = (x, x / 9 * 16)
    MDApp.title = "Fitness App"

    def on_start(self):
        pass

    def build(self):
        # Add screens to screen manager
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "DeepPurple"
        #self.theme_cls.bg_dark = get_color_from_hex("#8c78ff")
        self.theme_cls.theme_style = "Light"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(InitialScreen(name="initial"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ForgotPasswordScreen(name="forgot"))
        sm.add_widget(VerifyUserScreen(name="verify"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ChangePasswordScreen(name="password"))
        #sm.current = "main"

        # Check if sign in required
        if user.check_access_token():
            print(True)
            sm.current = "main"
        else:
            print(False)

        return sm


if __name__ == '__main__':
    FitnessApp().run()
