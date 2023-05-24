import easygui as eg
import tkinter as tk
from tkinter import simpledialog
# myvar = easygui.enterbox("What, is your favorite color?")
# print(myvar)

def get_name():
    '''Asks the user to enter their name and returns it as a string value'''
    title_name = "Name input"
    msg_name = "Please enter your name"
    return eg.enterbox(msg_name, title_name)
    # root = tk.Tk()
    # root.withdraw()  # Hide the main window

    # # Create a simple dialog box with an input field
    # user_input = simpledialog.askstring("Input Dialog", "Enter your name:")
    # return user_input

def get_gender():
    '''Asks the user to pick the option that corresponds to their gender and returns it as a string value'''
    title_name = "Gender input"
    msg_name = "Please pick the option for your gender"
    return eg.buttonbox(msg_name, title_name, ["Male", "Female"])

def test_arousal():
    '''Asks the user to pick the option that corresponds to their arousal level and returns it as a int value'''

    msgArousal = "Which of the following pictures best describes your level of arousal?"
    titleArousal = "Arousal test"
    imageArousal = "Server\ML\SAMArousal.png"
    return eg.indexbox(msgArousal, titleArousal, ["1", "2", "3", "4", "5"], image = imageArousal) 

def get_age():
    '''Asks the user to enter their age and returns it as a string value'''

    title_name = "Age input"
    msg_name = "Please enter your age"
    return eg.enterbox(msg_name, title_name)

def test_valence():
    '''Asks the user to pick the option that corresponds to their valence level and returns it as a int value'''

    msgValence = "Which of the following pictures best describes your level of valence?"
    titleValence = "Valence test"
    imageValence = "Server\ML\SAMValence.png"
    return eg.indexbox(msgValence, titleValence, ["1", "2", "3", "4", "5"], image = imageValence)  

def get_stress():
    '''Asks the user to enter a value between 1 to 100 that corresponds to their stress level and returns it as a string value'''

    msg = "On a scale from 1 to 100, how stressed are you?"
    title = "Stress test"
    return eg.enterbox(msg, title)


def show_input_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Create a simple dialog box with an input field
    user_input = simpledialog.askstring("Input Dialog", "Enter your name:")

    if user_input is not None:
        print("User input:", user_input)
    else:
        print("No input provided")

show_input_dialog()