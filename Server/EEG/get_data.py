

import time

print("Printing data...")
while (True): 
    time.sleep(5)
    data_file = open("data.txt", "r")

    arr = data_file.read().split(",") 
    
    print("--------------------------")
    print("Engagement: " + arr[1])
    print("Excitement: "+ arr[3])
    print("Long term exitement: " + arr[4])
    print("Stress/Frustration: " + arr[6])
    print("Relaxation: " + arr[8])
    print("Interest/Affinity: " + arr[10])
    print("Focus: " + arr[12])
    print("-------------------------")
    
    
    print()
    
