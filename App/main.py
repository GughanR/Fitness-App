# உ
import kivy

from kivy.app import App
from kivy.resources import resource_find
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
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
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
import os, sys
from kivy.resources import resource_add_path, resource_find
import user
import json
import workout


class DialogBtn(MDFlatButton):
    pass


class CustomDialog(MDDialog):

    def __init__(self, **kwargs):
        self.buttons = [
            DialogBtn(),
        ]
        super().__init__(**kwargs)
        self.open()


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
                response = user.login(self.unInput.text, self.pwInput.text)

                if response.status_code != 200:
                    CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
                else:
                    print("logged in")
                    # Pass user details to AccountPage
                    try:
                        user_details = user.get_user_details()
                        AccountPage.nameText = user_details["full_name"]
                        AccountPage.emailText = user_details["email_address"]
                        AccountPage.unText = user_details["user_name"]
                        AccountPage.weightUnitDropDown.text = user_details["unit_weight"]
                    except Exception as e:
                        pass
                    # Change screen
                    self.manager.current = "main"

            except Exception as e:
                CustomDialog(text="Connection error")

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
                CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            else:
                CustomDialog(text="Password has been reset\n\nCheck your email")
        except Exception as e:
            CustomDialog(
                text="Connection error"
            )


class SignUpScreen(Screen):
    createAccountBtn = ObjectProperty(None)
    nameInput = ObjectProperty(None)
    emailInput = ObjectProperty(None)
    unInput = ObjectProperty(None)
    pwInput = ObjectProperty(None)
    dialog = None

    # verifyDialog = ObjectProperty(None)
    # codeInput = ObjectProperty(None)

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
                    widget_object.helper_text = widget_object.hint_text + " must not be empty"
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
                    CustomDialog(
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
                CustomDialog(
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
                CustomDialog(
                    text=json.loads(response.content.decode("utf-8"))["detail"]
                )

            else:
                CustomDialog(
                    text="Account created\n\nPlease login"
                )

                self.manager.transition.direction = "left"
                self.manager.current = "login"

        except ValueError:
            self.codeInput.helper_text = "Verification code must be a number"

        except Exception as e:
            print(e)
            CustomDialog(
                text="Connection failed"
            )


class MainScreen(Screen):
    pass


class AccountPage(MDScrollView):
    updateBtn = ObjectProperty(None)
    nameInput = ObjectProperty(None)
    emailInput = ObjectProperty(None)
    unInput = ObjectProperty(None)
    weightUnitDropDown = ObjectProperty(None)
    # pwInput = ObjectProperty(None)
    dialog = None
    # verifyDialog = ObjectProperty(None)
    # codeInput = ObjectProperty(None)
    user_details = None

    # https://www.youtube.com/watch?v=6oHfaY6p0K0
    def show_drop_down(self):
        self.list_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "KG",
                "halign": "center",
                "on_release": lambda x="KG": self.update_weight_unit("KG")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "LB",
                "on_release": lambda x="LB": self.update_weight_unit("LB")
            }
        ]
        self.drop_down = MDDropdownMenu(
            caller=self.weightUnitDropDown,
            items=self.list_items,
            width_mult=2
        )
        self.drop_down.open()

    def update_weight_unit(self, weight_unit):
        self.weightUnitDropDown.text = weight_unit
        self.drop_down.dismiss()
        # Update in server
        response = user.update_weight_unit(weight_unit)

        try:
            if response.status_code != 200:
                CustomDialog(text=response.content.decode("utf-8")["detail"])
        except:
            CustomDialog(text="Connection error")

    # Set values for current details (runs when user already logged in)
    try:
        user_details = user.get_user_details()
        nameText = user_details["full_name"]
        emailText = user_details["email_address"]
        unText = user_details["user_name"]
        weightUnitDropDown.text = user_details["unit_weight"]

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
            self.weightUnitDropDown.text = user_details["unit_weight"]

        except Exception as e:
            print(e)
            CustomDialog(text="Connection failed")

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
                    widget_object.helper_text = widget_object.hint_text + " must not be empty"
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
                    CustomDialog(
                        text=json.loads(response.content.decode("utf-8"))["detail"]
                    )

                else:
                    CustomDialog(
                        text="Successfully updated"
                    )


            except:
                CustomDialog(
                    text="Connection failed"
                )

    def logout(self):
        try:
            response = user.logout()
            if response.status_code not in (200, 403):
                CustomDialog(
                    text="Unable to logout"
                )
            else:
                # Open initial screen
                MDApp.get_running_app().root.transition.direction = "right"
                MDApp.get_running_app().root.current = "initial"

        except Exception as e:
            CustomDialog(
                text="Connection error"
            )


class ChangePasswordScreen(Screen):  # TODO add password check
    dialog = ObjectProperty(None)

    def reset_inputs(self):
        for widget_name, widget_object in self.ids.items():
            if "Input" in widget_name:
                widget_object.text = ""
                widget_object.helper_text = ""

    def update_account(self):
        old_pw = self.ids.oldPWInput.text
        new_pw = self.ids.newPWInput.text
        response = user.check_password(new_pw)

        if response != True:
            self.ids.newPWInput.helper_text = response
            return

        try:
            response = user.update_password(old_pw, new_pw)
            if response.status_code != 200:
                CustomDialog(
                    text=json.loads(response.content.decode("utf-8"))["detail"]
                )
            else:
                CustomDialog(text="Password updated")

        except:
            CustomDialog(text="Connection failed")


class WorkoutPage(MDScrollView):
    def new_workout(self):
        MDApp.get_running_app().root.transition.direction = "left"
        MDApp.get_running_app().root.current = "create_workout"


class CreateWorkoutScreen(Screen):
    goalDropDown = ObjectProperty(None)
    typeDropDown = ObjectProperty(None)
    numOfDaysInput = ObjectProperty(None)

    def show_goal_drop_down(self):
        self.list_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Size",
                "halign": "center",
                "on_release": lambda x="Size": self.update_goal("Size")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Strength",
                "on_release": lambda x="Strength": self.update_goal("Strength")
            }
        ]
        self.drop_down = MDDropdownMenu(
            caller=self.goalDropDown,
            items=self.list_items,
            width_mult=2
        )
        self.drop_down.open()

    def update_goal(self, text):
        self.goalDropDown.text = text
        self.drop_down.dismiss()

    def show_type_drop_down(self):
        self.list_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Full Body",
                "halign": "center",
                "on_release": lambda x="Full Body": self.update_type("Full Body")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Upper Lower",
                "on_release": lambda x="Upper Lower": self.update_type("Upper Lower")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Push Pull Legs",
                "on_release": lambda x="Push Pull Legs": self.update_type("Push Pull Legs")
            }
        ]
        self.drop_down = MDDropdownMenu(
            caller=self.goalDropDown,
            items=self.list_items,
            width_mult=3
        )
        self.drop_down.open()

    def update_type(self, text):
        self.typeDropDown.text = text
        self.drop_down.dismiss()

    def create_workout_plan(self):
        # Check exercises are compatible with plan type
        # First get muscles chosen into list
        muscles_chosen = []
        for widget_name, widget_object in self.ids.items():
            if "chip" in widget_name:
                if widget_object.active:
                    muscles_chosen.append(widget_object.text.lower())
        valid = workout.check_plan_type(self.typeDropDown.text.lower(), muscles_chosen)
        if not valid:
            CustomDialog(text="Invalid Plan Type and Muscles combination")
            return

        # Check num of days chosen is valid
        try:
            days_input = int(self.numOfDaysInput.text)
        except ValueError:
            days_input = 0
        days_valid = workout.check_num_of_days(self.typeDropDown.text.lower(), days_input)
        if not days_valid[0]:
            CustomDialog(text=f"Number of days must be at least {days_valid[1]}")
            return

        # Create workout plan
        print(self.ids.planNameInput.text)
        print(self.goalDropDown.text)
        print(self.typeDropDown.text)


class FitnessApp(MDApp):
    Builder.load_file("My.kv")  # Load kivy file into main.py

    x = 700
    Window.size = (x, x / 9 * 16)
    MDApp.title = "Fitness App"
    # Set font sizes
    font_size_coefficient = Window.size[0] / 500
    fs_title = NumericProperty(font_size_coefficient * 80)
    fs_heading = NumericProperty(font_size_coefficient * 55)
    fs_normal = NumericProperty(font_size_coefficient * 30)

    # Set colour
    accent_colour = "#5542ff"

    def on_start(self):
        pass

    def build(self):
        # Add screens to screen manager
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "DeepPurple"
        # self.theme_cls.bg_dark = get_color_from_hex("#8c78ff")
        self.theme_cls.theme_style = "Light"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(InitialScreen(name="initial"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ForgotPasswordScreen(name="forgot"))
        sm.add_widget(VerifyUserScreen(name="verify"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ChangePasswordScreen(name="password"))
        sm.add_widget(CreateWorkoutScreen(name="create_workout"))
        # sm.current = "main"

        # Check if sign in required
        if user.check_access_token():
            sm.current = "create_workout"
        else:
            print(False)
        # sm.current = "main"  # DEBUG
        # sm.screens[5].children[0].children[1].current = "Account"  # DEBUG
        return sm


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    FitnessApp().run()
