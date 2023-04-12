# உ
import datetime

import kivy
import numpy as np

from kivy.app import App
from kivy.resources import resource_find
from kivymd.app import MDApp
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, OptionProperty
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
from kivy.utils import get_color_from_hex, platform
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
import os, sys
from kivy.resources import resource_add_path, resource_find
import user
import json
import workout
from kivymd.uix.card.card import MDCardSwipe, MDCardSwipeFrontBox, MDCardSwipeLayerBox, MDSeparator, MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from matplotlib import pyplot as plt
import view_progress


class DialogBtn(MDFlatButton):
    pass


class CustomDialog(MDDialog):

    def __init__(self, **kwargs):
        self.buttons = [
            DialogBtn(),
        ]
        super().__init__(**kwargs)
        self.open()


class WorkoutPlanCard(MDCardSwipe):
    text = StringProperty()
    image_source = StringProperty()
    workout_plan = ObjectProperty()


class WorkoutCard(MDCardSwipe):
    text = StringProperty()
    number = StringProperty()
    workout = ObjectProperty()


class ExerciseCard(MDCardSwipe):
    text = StringProperty()
    image_source = StringProperty()
    exercise = ObjectProperty()


class ExerciseCardNormal(MDCard):
    text = StringProperty()
    image_source = StringProperty()
    exercise = ObjectProperty()


class CompleteExerciseCard(MDCard):
    text = StringProperty()
    image_source = StringProperty()


class MuscleGroupButton(MDFlatButton):
    text = StringProperty()


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
    def on_pre_enter(self, *args):
        # Loads widgets in main menu screens
        # Account Page
        name_text = self.children[0].children[1].screens[2].children[0].nameInput.text
        if name_text == "":  # Only refresh if text field is empty
            AccountPage.refresh(self.children[0].children[1].screens[2].children[0])

        # Workouts Page
        # Get number of cards shown on screen
        cards_on_screen = self.children[0].children[1].screens[1].children[0].children[0].children[0].children
        if len(cards_on_screen) == 0:  # Only refresh if no cards on screen
            WorkoutPage.refresh(self.children[0].children[1].screens[1].children[0])

        # # View Progress Page
        # # Load dummy graph
        # stat_text = self.children[0].children[1].screens[0].children[0].statDropDown.text
        # if stat_text == "None":
        #     ViewProgressPage.g(self.children[0].children[1].screens[0].children[0])


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

    def remove_all_cards(self):
        self.ids.workoutsList.clear_widgets()

    def refresh(self):
        # Get Workout
        try:
            response = workout.get_workout_plans()
        except:
            CustomDialog(text="Connection failed")
            return

        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
            return

        # Convert response str to list
        response_list = json.loads(response.content.decode("utf-8"))

        # Convert list to objects
        workout_plans_list = []
        for item in response_list:
            workout_plans_list.append(workout.convert_workout_plan(item))

        # Display each workout plan
        self.remove_all_cards()  # Remove old cards
        for workout_plan_obj in workout_plans_list:
            card = WorkoutPlanCard(
                text=workout_plan_obj.workout_plan_name,
                image_source="Images/dumbbell_icon.png",
                workout_plan=workout_plan_obj
            )
            self.ids.workoutsList.add_widget(card)

    def remove_card(self, instance):
        # Delete workout plan
        try:
            response = workout.delete_workout_plan(instance.workout_plan)
        except:
            CustomDialog(text="Connection failed")
            return

        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
        else:
            self.ids.workoutsList.remove_widget(instance)
            CustomDialog(text=f"Deleted Workout Plan: \n{instance.workout_plan.workout_plan_name}")

    def select_card(self, instance):
        # Make sure that user intended to click not swipe
        if instance.state == "opened":
            return
        # Get plan details from server
        try:
            response = workout.get_workouts_in_plan(instance.workout_plan.workout_plan_id)
        except:
            CustomDialog(text="Connection failed")
            return
        # If error display error message
        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
            return
        # Convert response str to list
        response_list = json.loads(response.content.decode("utf-8"))
        converted_list = []
        for item in response_list:
            converted_list.append(workout.convert_workout(item))
        # Save list in workout plan
        instance.workout_plan.workout_list = converted_list
        # If no error, then open workout plan
        # https://stackoverflow.com/questions/30253745/python-for-kivypass-values-between-multiple-screens
        MDApp.get_running_app().root.get_screen("view_workouts").workout_plan = instance.workout_plan
        MDApp.get_running_app().root.transition.direction = "left"
        MDApp.get_running_app().root.current = "view_workouts"


class CreateWorkoutScreen(Screen):
    goalDropDown = ObjectProperty(None)
    typeDropDown = ObjectProperty(None)
    numOfDaysInput = ObjectProperty(None)

    def on_pre_enter(self, *args):
        # Clear inputs previously entered
        for widget_name, widget_object in self.ids.items():
            # Text Inputs
            if "Input" in widget_name:
                widget_object.text = ""
            # Exercise Chips
            elif "chip" in widget_name:
                widget_object.active = True
        # Drop Downs
        self.ids.goalDropDown.text = "Size"
        self.ids.typeDropDown.text = "Full Body"

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

        # Check plan name is valid
        valid = workout.check_plan_name(self.ids.planNameInput.text)
        if type(valid) == str:
            CustomDialog(text=valid)
            return

        # Create workout plan
        new_workout_plan = workout.create_workout_plan(
            plan_goal=self.goalDropDown.text.lower(),
            muscles_chosen=muscles_chosen,
            plan_type=self.typeDropDown.text.lower(),
            plan_name=self.ids.planNameInput.text,
            num_of_days=int(self.ids.numOfDaysInput.text)
        )
        # TODO: Show user plan before saving
        response = workout.save_new_plan(new_workout_plan)
        if response.status_code != 200:
            CustomDialog(text="Connection failed")
        else:
            CustomDialog(text="New Workout Created")
            MDApp.get_running_app().root.transition.direction = "right"
            MDApp.get_running_app().root.current = "main"


class ViewWorkoutsScreen(Screen):
    workout_plan = workout.WorkoutPlan()

    def on_pre_enter(self, *args):  # Load screen details on screen load
        self.ids.planName.text = str(self.workout_plan.workout_plan_name)
        self.refresh()

    def remove_all_cards(self):
        self.ids.workoutsInPlanList.clear_widgets()

    def remove_card(self, instance):
        # Delete workout
        try:
            response = workout.delete_workout(instance.workout)
        except:
            CustomDialog(text="Connection failed")
            return

        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
            return
        else:
            self.ids.workoutsInPlanList.remove_widget(instance)
            CustomDialog(text=f"Deleted Workout: \n{instance.workout.workout_name}")
        self.refresh()

    def refresh(self):
        # Get Workouts
        # Get plan details from server
        try:
            response = workout.get_workouts_in_plan(self.workout_plan.workout_plan_id)
        except:
            CustomDialog(text="Connection failed")
            return
        # If error display error message
        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
            return
        # Convert response str to list
        response_list = json.loads(response.content.decode("utf-8"))

        # Convert list to objects
        workouts_list = []
        for item in response_list:
            workouts_list.append(workout.convert_workout(item))
        # Save new details
        self.workout_plan.workout_list = workouts_list

        # Display each workout plan
        self.load_cards()

    def load_cards(self):
        # Remove previous cards
        self.remove_all_cards()
        # Display each workout plan
        workouts_list = self.workout_plan.workout_list
        for workout_obj in workouts_list:
            card = WorkoutCard(
                text=workout_obj.workout_name,
                number=str(workout_obj.workout_number),
                workout=workout_obj
            )
            self.ids.workoutsInPlanList.add_widget(card)

    def select_card(self, instance):
        # Make sure that user intended to click not swipe
        if instance.state == "opened":
            return
        # Get workout details from server
        try:
            response = workout.get_exercises_in_workout(instance.workout.workout_id)
        except:
            CustomDialog(text="Connection failed")
            return
        # If error display error message
        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
            return
        # Convert response str to list
        response_list = json.loads(response.content.decode("utf-8"))
        converted_list = []
        for item in response_list:
            converted_list.append(workout.convert_exercise(item))
        # Save list in workout
        instance.workout.exercise_list = converted_list
        # If no error, then open workout
        # https://stackoverflow.com/questions/30253745/python-for-kivypass-values-between-multiple-screens
        MDApp.get_running_app().root.get_screen("view_exercises").workout = instance.workout
        MDApp.get_running_app().root.transition.direction = "left"
        MDApp.get_running_app().root.current = "view_exercises"

    def add_workout(self):
        MDApp.get_running_app().root.get_screen("add_workout").workout_plan = self.workout_plan
        MDApp.get_running_app().root.transition.direction = "left"
        MDApp.get_running_app().root.current = "add_workout"


class ViewExercisesScreen(Screen):
    workout = workout.Workout()

    def on_pre_enter(self, *args):  # Load screen details on screen load
        self.ids.workoutName.text = str(self.workout.workout_name)
        self.refresh()

    def remove_all_cards(self):
        self.ids.exercisesInWorkoutList.clear_widgets()

    def remove_card(self, instance):
        # Delete exercise
        try:
            response = workout.delete_exercise(instance.exercise)
        except:
            CustomDialog(text="Connection failed")
            return

        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
        else:
            self.ids.exercisesInWorkoutList.remove_widget(instance)
            CustomDialog(text=f"Deleted Exercise: \n{instance.exercise.exercise_name.title()}")

    def refresh(self):
        # Get Workout Exercises
        # Get workout details from server
        try:
            response = workout.get_exercises_in_workout(self.workout.workout_id)
        except:
            CustomDialog(text="Connection failed")
            return
        # If error display error message
        if response.status_code != 200:
            CustomDialog(
                text=json.loads(response.content.decode("utf-8"))["detail"]
            )
            return
        # Convert response str to list
        response_list = json.loads(response.content.decode("utf-8"))

        # Convert list to objects
        exercises_list = []
        for item in response_list:
            exercises_list.append(workout.convert_exercise(item))
        # Save new details
        self.workout.exercise_list = exercises_list

        # Display each workout plan
        self.load_cards()

    def load_cards(self):
        # Remove previous cards
        self.remove_all_cards()
        # Display each workout plan
        exercises_list = self.workout.exercise_list

        for exercise_obj in exercises_list:
            card = ExerciseCard(
                text=exercise_obj.exercise_name.title(),
                image_source=f"Images/exercises/{exercise_obj.exercise_name.lower()}.png",
                exercise=exercise_obj
            )
            self.ids.exercisesInWorkoutList.add_widget(card)

    def select_card(self, instance):
        pass

    def complete_workout(self):
        # Change screen
        MDApp.get_running_app().root.get_screen("complete_workout").workout_obj = self.workout
        MDApp.get_running_app().root.transition.direction = "left"
        MDApp.get_running_app().root.current = "complete_workout"


class EditWorkoutPlanScreen(Screen):
    workout_plan = workout.WorkoutPlan()

    def on_pre_enter(self, *args):
        # Show current details
        # Get details from ViewWorkoutsScreen
        self.workout_plan = MDApp.get_running_app().root.get_screen("view_workouts").workout_plan

        # Set plan name
        self.ids.planNameInput.text = str(self.workout_plan.workout_plan_name)
        # Set plan goal
        self.ids.goalDropDown.text = str(self.workout_plan.workout_plan_goal).title()

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
            caller=self.ids.goalDropDown,
            items=self.list_items,
            width_mult=2
        )
        self.drop_down.open()

    def update_goal(self, text):
        self.ids.goalDropDown.text = text
        self.drop_down.dismiss()

    def update_workout_plan(self):
        # Check plan name
        valid = workout.check_plan_name(self.ids.planNameInput.text)
        if type(valid) == str:
            CustomDialog(text=valid)
            return
        # Get new variables
        self.workout_plan.workout_plan_name = self.ids.planNameInput.text
        self.workout_plan.workout_plan_goal = self.ids.goalDropDown.text.lower()
        # Send request
        try:
            response = workout.update_workout_plan(self.workout_plan)
        except:
            CustomDialog(text="Connection error")
            return
        # Output error message
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
        else:
            # Output success message
            CustomDialog(text="Updated Workout Plan")


class EditWorkoutScreen(Screen):
    workout = workout.Workout()

    def on_pre_enter(self, *args):
        # Show current details
        # Get details from ViewWorkoutsScreen
        self.workout = MDApp.get_running_app().root.get_screen("view_exercises").workout
        # Set workout name
        self.ids.workoutNameInput.text = str(self.workout.workout_name)

    def update_workout(self):
        # Check workout name
        valid = workout.check_plan_name(self.ids.workoutNameInput.text)
        if type(valid) == str:
            CustomDialog(text=valid)
            return
        # Get new variable
        self.workout.workout_name = self.ids.workoutNameInput.text
        # Send request
        try:
            response = workout.update_workout(self.workout)
        except:
            CustomDialog(text="Connection error")
            return
        # Output error message
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
        else:
            # Output success message
            CustomDialog(text="Updated Workout")


class AddWorkoutScreen(Screen):
    workout_plan = workout.WorkoutPlan()

    def add_workout(self):
        # Check workout name
        valid = workout.check_plan_name(self.ids.workoutNameInput.text)
        if type(valid) == str:
            CustomDialog(text=valid)
            return
        # Create workout object
        # Calculate workout number
        workout_number = len(self.workout_plan.workout_list)
        new_workout = workout.Workout(
            {
                "workout_number": workout_number,
                "workout_name": self.ids.workoutNameInput.text
            }
        )
        # If name valid then send request
        try:
            response = workout.add_workout(new_workout, self.workout_plan.workout_plan_id)
        except:
            CustomDialog(text="Connection error")
            return
        # Output error message
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return
        else:
            # Output success message
            CustomDialog(text="Added Workout")
        # Change screen
        MDApp.get_running_app().root.transition.direction = "right"
        MDApp.get_running_app().root.current = "view_workouts"


class MuscleGroupsScreen(Screen):
    def on_pre_enter(self, *args):
        self.clear_screen()
        # Get exercises from server
        try:
            response = workout.get_exercises()
        except:
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return

        exercises_json = json.loads(response.content.decode("utf-8"))
        exercises = workout.load_exercises(exercises_json)

        # Get distinct muscle groups
        muscle_groups = set()
        for exercise in exercises:
            muscle_groups.add(exercise.muscle_group)
        # Sort in alphabetical order
        muscle_groups = sorted(muscle_groups)

        # Output each muscle group as a button
        for muscle_group in muscle_groups:
            button = MuscleGroupButton(
                text=muscle_group.title()
            )
            self.ids.muscleGroupsList.add_widget(button)

    def clear_screen(self):
        self.ids.muscleGroupsList.clear_widgets()

    def select_button(self, instance):
        # If a button is pressed show next screen with exercises from selected muscle group
        muscle_group_selected = instance.text
        # Change screen
        MDApp.get_running_app().root.get_screen("add_exercise").muscle_group = muscle_group_selected
        MDApp.get_running_app().root.transition.direction = "left"
        MDApp.get_running_app().root.current = "add_exercise"

    def refresh(self):
        self.on_pre_enter()


class AddExerciseScreen(Screen):
    muscle_group = StringProperty()

    def on_pre_enter(self, *args):
        self.clear_screen()
        # Get exercises from server
        try:
            response = workout.get_exercises()
        except:
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return

        exercises_json = json.loads(response.content.decode("utf-8"))
        exercises = workout.load_exercises(exercises_json)

        # https://www.pythontutorial.net/python-basics/python-filter-list/
        muscle_group_exercises = filter(lambda e: e.muscle_group == self.muscle_group.lower(), exercises)

        # Get distinct muscle sub groups
        muscle_subgroups = set()
        for exercise in muscle_group_exercises:
            muscle_subgroups.add(exercise.muscle_subgroup)
        # Sort in alphabetical order
        muscle_subgroups = sorted(muscle_subgroups)

        # Output exercises for each muscle subgroup
        for group in muscle_subgroups:
            # Add heading
            if group.lower() != self.muscle_group.lower():
                heading = MDLabel(
                    text=group.title()
                )
                heading.font_size = MDApp.get_running_app().fs_normal
                heading.adaptive_height = True

                self.ids.exercisesList.add_widget(heading)
                self.ids.exercisesList.add_widget(MDSeparator())
            # Add exercises
            # Filter subgroup
            subgroup_exercises = [e for e in exercises if e.muscle_subgroup == group.lower()]
            # Sort
            subgroup_exercises = sorted(subgroup_exercises, key=lambda e: e.exercise_name)
            for exercise in subgroup_exercises:
                card = ExerciseCardNormal(
                    text=exercise.exercise_name.title(),
                    image_source=f"Images/exercises/{exercise.exercise_name.lower()}.png",
                    exercise=exercise
                )
                self.ids.exercisesList.add_widget(card)

            self.ids.exercisesList.add_widget(MDLabel())  # Adds extra space

    def clear_screen(self):
        self.ids.exercisesList.clear_widgets()

    def select_card(self, instance):
        # If a card is pressed add exercise
        # Get details
        workout_obj = MDApp.get_running_app().root.get_screen("view_exercises").workout
        # Calculate exercise num
        exercise_num = len(workout_obj.exercise_list)
        instance.exercise.workout_exercise_number = exercise_num

        try:
            response = workout.add_workout_exercise(instance.exercise, workout_obj.workout_id)
        except:
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
        else:
            CustomDialog(text=f"Added {instance.exercise.exercise_name.title()} to {workout_obj.workout_name}")
            MDApp.get_running_app().root.transition.direction = "right"
            MDApp.get_running_app().root.current = "view_exercises"

    def refresh(self):
        self.on_pre_enter()


class CompleteWorkoutScreen(Screen):
    workout_obj = workout.Workout()
    exercise_queue = []
    exercise_number = 1
    set_number = 1
    exercise_history_id = 0
    last_set = workout.ExerciseHistory()
    goal = StringProperty()
    exercise_history = []

    def on_enter(self, *args):
        # Set title
        self.ids.title.text = self.workout_obj.workout_name

        # Get goal from workouts screen
        self.goal = MDApp.get_running_app().root.get_screen("view_workouts").workout_plan.workout_plan_goal

        # Create exercise_queue
        # Get exercises from server
        exercises = self.workout_obj.exercise_list

        # Group exercises in terms of muscle group
        grouped_exercises = sorted(exercises, key=lambda e: e.muscle_group)
        exercise_queue = []
        for exercise in grouped_exercises:
            if exercise.compound:
                exercise_queue.insert(0, exercise)
            else:
                exercise_queue.append(exercise)

        # Save exercise queue
        self.exercise_queue = exercise_queue

        # Show first exercise
        self.show_exercise()

        # Show weight unit
        self.ids.weightUnit.text = user.get_user_details()["unit_weight"]

    def on_pre_leave(self, *args):
        # Reset inputs and variables
        self.output_weight_reps("", "")
        self.set_number = 1
        self.workout_obj = workout.Workout()
        self.exercise_queue = []
        self.exercise_number = 1
        self.set_number = 1
        self.exercise_history_id = 0
        self.last_set = workout.ExerciseHistory()
        self.goal = ""
        self.exercise_history = []
        self.ids.set.text = f"[b]Set {self.set_number}[/b]"
        self.ids.skipBtn.disabled = False

    def show_exercise(self):
        exercise_card = CompleteExerciseCard(
            text=f"{self.exercise_queue[0].exercise_name} ({self.exercise_number}/{len(self.workout_obj.exercise_list)})",
            image_source=f"Images/exercises/{self.exercise_queue[0].exercise_name}.png"
        )
        self.ids.exerciseBox.clear_widgets()
        self.ids.exerciseBox.add_widget(exercise_card)
        # Show new recommended weight and reps
        self.calculate_weight_reps()

    def skip_exercise(self):
        exercise = self.exercise_queue.pop(0)
        self.exercise_queue.append(exercise)
        # Reset set number
        self.set_number = 1
        self.show_exercise()

    def finish_exercise(self):
        self.exercise_queue.pop(0)

        if self.check_workout_complete():
            CustomDialog(text="Workout Completed!")
            MDApp.get_running_app().root.transition.direction = "right"
            MDApp.get_running_app().root.current = "main"
            return

        self.exercise_number += 1
        self.show_exercise()
        # Enable skip button
        self.ids.skipBtn.disabled = False
        # Reset set number
        self.set_number = 1
        self.ids.set.text = f"[b]Set {self.set_number}[/b]"

    def check_workout_complete(self):
        if len(self.exercise_queue) == 0:
            return True
        else:
            return False

    def get_history(self):
        # Get history for current exercise
        try:
            current_exercise = self.exercise_queue[0]
            response = workout.get_exercise_history(current_exercise.exercise_id)
        except:
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return
        history_json = json.loads(response.content.decode("utf-8"))
        # Save history
        self.exercise_history = workout.convert_exercise_history(history_json)

    def save_set(self):
        # Get inputs
        weight_input = self.ids.weightInput.text
        reps_input = self.ids.repsInput.text
        # Check inputs
        if not workout.check_weight_input(weight_input):
            CustomDialog(text="Invalid Weight")
            return
        if not workout.check_reps_input(reps_input):
            CustomDialog(text="Invalid Repetitions")
            return

        # Save set in database
        # If set number 1 create workout exercise history
        if self.set_number == 1:
            try:
                current_exercise = self.exercise_queue[0]
                response = workout.add_workout_exercise_history(current_exercise.workout_exercise_id)
            except:
                CustomDialog(text="Connection error")
                return
            if response.status_code != 200:
                CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
                return
            else:
                self.exercise_history_id = json.loads(response.content.decode("utf-8"))["exercise_history_id"]
        # Save set history
        try:
            current_exercise = self.exercise_queue[0]
            response = workout.add_set_history(
                self.exercise_history_id,
                self.set_number,
                int(reps_input),
                float(weight_input),
                self.ids.weightUnit.text
            )
        except:  # Check for error
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return
        else:
            CustomDialog(text=f"Saved Set {self.set_number}")
        # Clear inputs
        self.ids.weightInput.text = ""
        self.ids.repsInput.text = ""
        # Increase set number by 1
        self.set_number += 1
        self.ids.set.text = f"[b]Set {self.set_number}[/b]"
        # Disable skip button
        self.ids.skipBtn.disabled = True
        # Save to last_set
        if self.ids.weightUnit.text != "KG":  # Convert to KG
            weight_used = float(weight_input)/2.205
        else:
            weight_used = float(weight_input)
        self.last_set = workout.ExerciseHistory(
            {
                "weight_used": weight_used,
                "reps_completed": int(reps_input)
            }
        )
        # Show new recommended weight and reps
        self.calculate_weight_reps()

    def calculate_weight_reps(self):
        self.get_history()
        exercise_history = self.exercise_history

        # Convert to KG
        for e in exercise_history:
            if e.unit_weight != "KG":
                e.weight_used = e.weight_used/2.205
        # If no history, then output nothing
        if len(exercise_history) == 0:
            self.output_weight_reps("", "")
            return

        # Get number of workouts
        # Exercise in workout can only have one occurrence where set number = 1
        total_workouts = len([e for e in exercise_history if e.set_number == 1])

        # Do simpler calculation if less than 5 workouts
        if total_workouts < 5:
            min_reps, max_reps = workout.exercise_reps(self.exercise_queue[0], self.goal)

            if self.set_number == 1:
                # Get previous reps and weight used from last workout
                first_set_history = [e for e in exercise_history if e.set_number == 1]
                previous_reps = first_set_history[-1].reps_completed
                previous_weight = first_set_history[-1].weight_used

                if previous_reps < max_reps:
                    reps = previous_reps + 1
                    weight = previous_weight
                else:
                    reps = min_reps
                    weight = previous_weight + 2
            else:
                # Use reps and weight from last set
                reps = self.last_set.reps_completed
                weight = self.last_set.weight_used
        else:
            # Calculate weight using algorithm
            # Using self.exercise_history because function will convert to KG again
            weight = workout.calculate_weight(
                self.exercise_queue[0],
                self.exercise_history,
                self.set_number,
                self.last_set,
                self.goal
            )
            reps = workout.calculate_reps(
                self.exercise_queue[0],
                self.exercise_history,
                self.set_number,
                weight,
                self.last_set,
                self.goal
            )

        # Output
        self.output_weight_reps(round(weight, 2), int(reps))

    def output_weight_reps(self, weight, reps):
        # Convert from KG
        if self.ids.weightUnit.text != "KG":
            self.ids.weightInput.text = str(weight*2.205)
        else:
            self.ids.weightInput.text = str(weight)
        self.ids.repsInput.text = str(reps)


class ViewProgressPage(MDScrollView):
    statDropDown = ObjectProperty()
    date_range = []
    exercises = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def show_date_picker(self):
        self.date_dialog = MDDatePicker(
            mode="range",
            primary_color="#5542ff",
            text_button_color="#5542ff",
            selector_color="#5542ff"
        )
        self.date_dialog.bind(
            on_save=self.save_date
        )
        self.date_dialog.open()

    def draw_graph(self, graph):
        self.ids.graphBox.clear_widgets()
        self.ids.graphBox.add_widget(FigureCanvasKivyAgg(graph))

    def process_stats(self):
        statistic = self.ids.statDropDown.text.lower()
        start_date = self.date_range[0]
        end_date = self.date_range[-1]
        # Get exercise history
        try:
            # Get exercise id of selected exercise
            exercise_id = [e.exercise_id for e in self.exercises if e.exercise_name == statistic][0]
            response = workout.get_exercise_history(exercise_id)
        except:  # Check for error
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return

        history_json = json.loads(response.content.decode("utf-8"))

        # Save history
        exercise_history = workout.convert_exercise_history(history_json)
        # Convert weight to KG
        # Convert dates
        for e in exercise_history:
            if e.unit_weight != "KG":
                e.weight_used = e.weight_used/2.205

            date_time = e.date_completed.replace("T", " ")
            date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            e.date_completed = date_time.date()

        # Order list
        exercise_history = sorted(exercise_history, key=lambda e: e.date_completed)

        # Create x and y data
        x = []
        y = []

        # Get highest weight used in each workout
        for e in exercise_history:
            if e.date_completed not in x:
                x.append(e.date_completed)
                y.append(e.weight_used)
            else:
                original_index = x.index(e.date_completed)
                current_weight = y[original_index]
                if e.weight_used > current_weight:
                    y[original_index] = e.weight_used

        # Plot graph
        print(x, y)
        graph = view_progress.plot_graph(x, y, self.date_range)

        self.draw_graph(graph)








    def save_date(self, instance, value, date_range):
        # Output selected date
        self.ids.dateRange.text = instance.ids.label_full_date.text
        # Get start and end date
        start = date_range[0]
        end = date_range[-1]
        # Save date range list
        self.date_range = date_range

    def show_statistics(self):
        # Get exercises from server
        try:
            response = workout.get_exercises()
        except:
            CustomDialog(text="Connection error")
            return
        if response.status_code != 200:
            CustomDialog(text=json.loads(response.content.decode("utf-8"))["detail"])
            return

        exercises_json = json.loads(response.content.decode("utf-8"))
        exercises = workout.load_exercises(exercises_json)

        # Order exercises
        exercises = sorted(exercises, key=lambda e: e.exercise_name)
        # Save exercises locally
        self.exercises = exercises

        # Create Drop down items
        self.list_items = []
        # Add each exercise item
        for exercise in exercises:
            name = exercise.exercise_name.title()
            item = {
                "viewclass": "OneLineListItem",
                "text": name,
                "halign": "center",
                "on_release": lambda x=name: self.update_stat(x)
            }
            self.list_items.append(item)

        # Drop down settings
        self.drop_down = MDDropdownMenu(
            caller=self.ids.statDropDown,
            items=self.list_items,
            width_mult=4
        )
        self.drop_down.open()

    def update_stat(self, text):
        self.ids.statDropDown.text = text.title()
        self.drop_down.dismiss()


class FitnessApp(MDApp):
    Builder.load_file("My.kv")  # Load kivy file into main.py

    x = 783
    # Following window options for debugging
    # It does not change anything when running on mobile
    Window.size = (x, x / 9 * 16)
    Window.top = 0
    Window.left = 0
    Window.borderless = True
    Window.softinput_mode = "below_target"
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
        self.theme_cls.material_style = "M3"
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
        sm.add_widget(ViewWorkoutsScreen(name="view_workouts"))
        sm.add_widget(ViewExercisesScreen(name="view_exercises"))
        sm.add_widget(EditWorkoutPlanScreen(name="edit_workout_plan"))
        sm.add_widget(EditWorkoutScreen(name="edit_workout"))
        sm.add_widget(AddWorkoutScreen(name="add_workout"))
        sm.add_widget(MuscleGroupsScreen(name="muscle_groups"))
        sm.add_widget(AddExerciseScreen(name="add_exercise"))
        sm.add_widget(CompleteWorkoutScreen(name="complete_workout"))
        # sm.current = "main"

        # Check if sign in required
        if user.check_access_token():
            sm.current = "main"
        # sm.current = "main"  # DEBUG
        # sm.screens[5].children[0].children[1].current = "Account"  # DEBUG
        return sm


if __name__ == '__main__':
    FitnessApp().run()
