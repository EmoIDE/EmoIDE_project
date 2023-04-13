import easygui as eg
# myvar = easygui.enterbox("What, is your favorite color?")
# print(myvar)

def get_name():
    title_name = "Name input"
    msg_name = "Please enter your name"
    return eg.enterbox(msg_name, title_name)

def get_gender():
    title_name = "Gender input"
    msg_name = "Please pick the option for your gender"
    return eg.buttonbox(msg_name, title_name, ["Male", "Female"])

def test_arousal():
    msgArousal = "Which of the following pictures best describes your level of arousal?"
    titleArousal = "Arousal test"
    imageArousal = "Server\ML\SAMArousal.png"
    return eg.indexbox(msgArousal, titleArousal, ["1", "2", "3", "4", "5"], image = imageArousal) 

def get_age():
    title_name = "Age input"
    msg_name = "Please enter your age"
    return eg.enterbox(msg_name, title_name)

def test_valence():

    msgValence = "Which of the following pictures best describes your level of valence?"
    titleValence = "Valence test"
    imageValence = "Server\ML\SAMValence.png"
    return eg.indexbox(msgValence, titleValence, ["1", "2", "3", "4", "5"], image = imageValence)  
