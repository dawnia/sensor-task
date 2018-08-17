
"""
Once the params are selected on an initial screen and the "start" button is pressed, the COGame class (within main.py) is instantiated.

The COGame.init() function then runs, and every 1/60th of a second the COGame.update() function runs. 

From there, the game reads from different sensors (here, touches on the screen) and decides what "state" the task is in. 

It has a state transition dictionary (self.FSM) that it cycles through depending on whether the subject has finished a trial, is still doing a trial, etc.

Code needs to write a) time, b) sensor values, c) trial number, d) trial type, e) trial state at every task loop

sampling rate 50hz
Connect to sensor input (ie know when it’s reset)
"""


# select conds
# name test file
# do we need to write to arduino?


import serial
import csv
import time
from datetime import datetime
from playsound import playsound

port = serial.Serial('/dev/tty.usbmodem1411', 9600)
time.sleep(2)   # 2 sec to establish connection with Arduino
numTrials = int(input('Enter number of trials to start\n'))

for trial in range(numTrials):    # four trials
	time_end = time.time() + 10
	playsound('beep.mp3')
	
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

port.close()


