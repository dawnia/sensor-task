
"""
Future protocol:

1. Select conditions
2. Select start
3. Instantiate game class
4. Run game init()
5. Run game update() at sampling rate (50 Hz)
6. Game reads from sensors and determines game state
7. Cycles through state transformation dictionary on state of each trial
8. Write a) time, b) sensor values, c) trial number, d) trial type, e) trial state at every task loop, start sound, end sound

Considerations
- How to save data the entire time, while managing the task? --> threading? a lot of calls? Two programs, match up times? Need to maintain 50 Hz
- need to write to Arduino?
- timing of conditions depends on task design
- functions
- Table
"""

import serial
import csv
import time
import pygame

class Experiment():

	def __init__(self, trial_len=5, my_port='/dev/tty.usbmodem1411'):
		self.trial_len = trial_len
		# self.trial_amt = int(input('Enter number of trials to start\n'))
		self.sound = False
		self.cur_state = 'init'
		self.my_port = my_port
		self.my_serial = self.connect_arduino()
		pygame.mixer.init()
		self.run_trials()

	def run_trials(self):
		# for trial_num in range(self.trial_amt):
		trial_num = 1
		start_time = time.time()
		while time.time() < start_time + 600:    # 10 min max
			next_task = str(input('Enter type number of next task or DONE to quit.\n'))
			if next_task == 'DONE':
				break
			else:
				self.cur_state = 'task_' + next_task
			print('Trial starting...')
			self.sound = pygame.mixer.get_busy()
			self.play_sound('start')
			time_end = time.time() + self.trial_len
			while time.time() < time_end:
				data = self.read_arduino()
				self.save_data(data, trial_num)
			self.play_sound('end')
			self.cur_state = 'btwn_task'
			print('Trial ended.')
			trial_num += 1
		self.my_serial.close()

	def connect_arduino(self):
		my_serial = serial.Serial(self.my_port, 9600)
		print('Connecting Arduino.')
		time.sleep(2)    # 2 sec to establish connection with Arduino
		return my_serial

	def read_arduino(self):
		''' Read sensor value from Arduino. '''
		data = self.my_serial.readline()
		data = data.decode('utf-8')    # bytes to string
		data = int(''.join(filter(str.isdigit, data)))    # extract digits
		return data

	def save_data(self, data, trial_num):
		''' Save data to csv. '''
		with open('test.csv', 'a') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow([time.time(), data, 'trial' + str(trial_num), self.cur_state, self.sound])

	def play_sound(self, state):
		if state == 'start':
			pygame.mixer.music.load('start_beep.mp3')
			pygame.mixer.music.play()
		elif state == 'end':
			pygame.mixer.music.load('end_beep.mp3')
			pygame.mixer.music.play()

Experiment()
