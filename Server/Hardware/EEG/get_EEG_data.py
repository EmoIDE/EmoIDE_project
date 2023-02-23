

import time

def get_EEG_data_print(arr):
    print("Printing data...")
    # data_file = open("data.txt", "r")

    # arr = data_file.read().split(",") 
        
    print("--------------------------")
    print("Engagement: " + arr[1])
    print("Excitement: "+ arr[3])
    print("Long term exitement: " + arr[4])
    print("Stress/Frustration: " + arr[6])
    print("Relaxation: " + arr[8])
    print("Interest/Affinity: " + arr[10])
    print("Focus: " + arr[12])
    print("-------------------------")
        
        
def get_EEG_data():
    data_file = open("C:\Users\sebastian.johanss11\Desktop\Python grejer\Faktisk EmoIDE\EmoIDE_project-1\Server\Hardware\EEG\data.txt", "r")

    data_arr = data_file.read().split(",")

    data_dict = {
        "Engagement": data_arr[1],
        "Excitement": data_arr[3],
        "Long term excitement": data_arr[4],
        "Stress/Frustration" : data_arr[6],
        "Relaxation": data_arr[8],
        "Interest/Affinity": data_arr[10],
        "Focus": data_arr[12]
        }

    return data_dict

get_EEG_data_print(get_EEG_data())

#data_arr = [met=["eng.isActive","eng","exc.isActive","exc","lex","str.isActive","str",
#"rel.isActive","rel","int.isActive","int","foc.isActive","foc"]]
        
    
