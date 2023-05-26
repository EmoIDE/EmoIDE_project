import easygui as eg

def get_name():
    '''Asks the user to enter their name and returns it as a string value'''
    title_name = "Name input"
    msg_name = "Please enter your name"
    return eg.enterbox(msg_name, title_name)

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


