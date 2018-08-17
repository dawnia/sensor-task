
"""
Future protocol:

1. Select conditions
2. Select start
3. Instantiate game class
4. Run game init()
5. Run game update() at sampling rate (50 Hz)
6. Game reads from sensors and determines game state
7. Cycles through state transformation dictionary on state of each trial
8. Write a) time, b) sensor values, c) trial number, d) trial type, e) trial state at every task loop

Considerations
- How to save data the entire time, while managing the task? --> threading
- need to write to Arduino?
- timing of conditions depends on task design
- Functions :D
"""

import serial
import csv
import time
from datetime import datetime
from playsound import playsound

# Connect to Arduino
port = serial.Serial('/dev/tty.usbmodem1411', 9600)
time.sleep(2)   # 2 sec to establish connection with Arduino

# Number of trials and trial length
numTrials = int(input('Enter number of trials to start\n'))
trial_len = 4

for trial in range(numTrials):

	time_end = time.time() + trial_len
	playsound('start_beep.mp3')
	
	while time.time() < time_end:   # the next 10 sec
	
		# read sensor value from Arduino
	    data = port.readline()
	    data = data.decode("utf-8")    # bytes to string
	    data = int(''.join(filter(str.isdigit, data)))
	    print(data)	  # extract digits

	    # save to csv
	    with open('test.csv', 'a') as f:
	    	writer = csv.writer(f, delimiter=',')
	    	curTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')
	    	writer.writerow([curTime, data, 'trial' + str(trial)])

	playsound('end_beep.mp3')
	time.sleep(1)

port.close()
