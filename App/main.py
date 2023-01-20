import kivy

from kivy.app import App
from kivy.resources import resource_find
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
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

import login
import json

Builder.load_file("My.kv")  # Load kivy file into main.py


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
        empty = False
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                if len(widget_object.text) == 0:
                    empty = True
                    widget_object.helper_text = widget_object.hint_text + " must not be empty"
        if not empty:
            try:
                response = login.login(self.unInput.text, self.pwInput.text)

                if response.status_code != 200:
                    self.dialog = MDDialog(
                        text=json.loads(response.content.decode("utf-8"))["detail"]
                    ) 
                    self.dialog.open()

            except Exception as e:
                self.dialog = MDDialog(
                    text=e
                ) 
                self.dialog.open()

        

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
            response = login.reset_password(email_address)
            if response.status_code != 200:
                self.dialog = MDDialog(
                    text=json.loads(response.content.decode("utf-8"))["detail"]
                ) 
                self.dialog.open()
            else:
                self.dialog = MDDialog(
                    text="Password has been reset\n\nCheck your email"
                ) 
                self.dialog.open()
        except Exception as e:
            self.dialog = MDDialog(
                    text=e
                ) 
            self.dialog.open()
            


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
                    response = login.check_name(widget_object.text)
                elif "email" in widget_name:
                    response = login.check_email(widget_object.text)
                elif "un" in widget_name:
                    response = login.check_username(widget_object.text)
                elif "pw" in widget_name:
                    response = login.check_password(widget_object.text)
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
                response = login.create_account(
                    self.nameInput.text,
                    self.emailInput.text,
                    self.unInput.text,
                    self.pwInput.text
                    )

                if response.status_code != 200:
                    self.dialog = MDDialog(
                        text="Server error"
                    )
                    self.dialog.open()
                else:
                    # Pass variables to verification screen
                    self.manager.screens[4].fullname = self.nameInput.text
                    self.manager.screens[4].email = self.emailInput.text
                    self.manager.screens[4].username = self.unInput.text
                    self.manager.screens[4].password = self.pwInput.text
                    self.manager.transition.direction = "left"
                    self.manager.current = "verify"

            except:
                self.dialog = MDDialog(
                    text="Connection failed"
                ) 
                self.dialog.open()
            

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
            response = login.verify(
                full_name=self.fullname,
                email_address=self.email,
                user_name=self.username,
                password=self.password,
                verification_code=int(self.codeInput.text)
            )
            if response.status_code != 200:
                self.dialog = MDDialog(
                    text=json.loads(response.content.decode("utf-8"))["detail"]
                ) 
                self.dialog.open()
            else:
                self.dialog = MDDialog(
                    text="Account created\n\nPlease login"
                ) 
                self.dialog.open()
                self.manager.transition.direction = "left"
                self.manager.current = "login"

        except ValueError:
            self.codeInput.helper_text = "Verification code must be a number"

        except Exception as e:
            print(e)
            self.dialog = MDDialog(
                    text="Connection failed"
                ) 
            self.dialog.open()

class FitnessApp(MDApp):
    x = 700
    Window.size = (x, x / 9 * 16)

    def on_start(self):
        pass

    def build(self):
        # Add screens to screen manager
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(InitialScreen(name="initial"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ForgotPasswordScreen(name="forgot"))
        sm.add_widget(VerifyUserScreen(name="verify"))

        # Check if sign in required
        if login.check_access_token():
            print(True)
            sm.current = "login"
        else:
            print(False)

        return sm


if __name__ == '__main__':
    FitnessApp().run()
