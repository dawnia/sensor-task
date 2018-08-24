
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
- Table (and can easily name columns)
- create new Processes for other sensing data
"""

import serial
import csv
import time
import pygame
import multiprocessing as mp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Experiment():

	def __init__(self, trial_len=5, my_port='/dev/tty.usbmodem1411'):
		self.trial_len = trial_len
		self.trial_num = 0
		self.sound = 0
		self.data_csv, self.states_csv, self.merged_csv, self.cur_time = self.generate_filenames()
		self.cur_state = 'init'
		self.change_state('init')
		self.my_port = my_port
		self.merged_df = pd.DataFrame()
		self.my_serial = self.connect_arduino()
		pygame.mixer.init()
		# self.tasks = ['off_angle_flat','off_angle_flat','off_angle_flat','off_angle_norm', 'off_angle_norm','off_angle_norm', 'torqued','torqued','torqued']
		self.tasks = [1,2,3]
		self.new_process()
		self.merge_csv()
		self.plot_merged()

	def run_trials(self, event):
		start_time = time.time()
		while self.trial_num < len(self.tasks) and time.time() < start_time + 600:    # 10 min max
			# input('Press enter to begin trial.\n')
			print('\nNext trial')
			# self.sound = pygame.mixer.get_busy()
			self.play_sound()
			self.change_state('task_' + str(self.tasks[self.trial_num]))

			time_end = time.time() + self.trial_len
			while time.time() < time_end:
				continue
			
			self.play_sound()
			self.change_state('btwn_trial')
			print('Trial ended.')
			time.sleep(3)    # time so that ending noise goes off
			self.trial_num += 1
		event.set()
		self.my_serial.close()

	def record_data(self, event):
		# time.sleep(3)    # to avoid ValueError from Arduino
		start_time = time.time()
		while time.time() < start_time + 600:
			data = self.read_arduino()
			if data:
				with open(self.data_csv, 'a') as f:
					writer = csv.writer(f, delimiter=',')
					writer.writerow([time.time(), data])
			if event.is_set():
				break

	def connect_arduino(self):
		my_serial = serial.Serial(self.my_port, 9600)
		print('Connecting Arduino.')
		# time.sleep(2)    # 2 sec to establish connection with Arduino
		return my_serial

	def read_arduino(self):
		''' Read sensor value from Arduino. '''
		self.my_serial.flushInput()
		data = self.my_serial.readline()
		data = data.decode('utf-8')    # bytes to string
		if any(char.isdigit() for char in data):
			data = int(''.join(filter(str.isdigit, data.strip())))    # extract digits
			return data

	def change_state(self, new_state):
		self.cur_state = new_state
		with open(self.states_csv, 'a') as f:
			writer = csv.writer(f, delimiter=',')
			writer.writerow([time.time(), self.cur_state, self.trial_num])

	def play_sound(self):
		# start trial
		if self.cur_state == 'init' or self.cur_state == 'btwn_trial':
			pygame.mixer.music.load('slowedstart.mp3')
			pygame.mixer.music.play()
		# end trial
		else:
			pygame.mixer.music.load('slowedend.mp3')
			pygame.mixer.music.play()

	def new_process(self):
		if __name__ == '__main__':
			event = mp.Event()
			record = mp.Process(target=self.record_data, args=(event,))
			record.start()
			time.sleep(3)
			self.run_trials(event)
			record.join()

	def generate_filenames(self):
		cur_time = time.strftime("%Y%m%d-%H%M%S")
		data_name = 'data_' + cur_time + '.csv'
		states_name = 'states_' + cur_time + '.csv'
		merged_name = 'merged_' + cur_time + '.csv'
		return data_name, states_name, merged_name, cur_time

	def merge_csv(self):
		data = pd.read_csv(self.data_csv, names=['time','ard_val'])
		states = pd.read_csv(self.states_csv, names=['time', 'state', 'trial_num'])
		self.merged_df = pd.merge_asof(data, states, on='time')
		self.merged_df.to_csv(self.merged_csv)

	def plot_merged(self):
		# shift seconds to 0
		self.merged_df[['time','ard_val']] = self.merged_df[['time','ard_val']].apply(pd.to_numeric)
		start_time = self.merged_df['time'].iloc[0]
		self.merged_df['time'] = self.merged_df['time'].apply(lambda r: r - start_time)
		# Arduino units --> Volts
		self.merged_df['ard_val'] = self.merged_df['ard_val'].apply(lambda r: r*0.0048828125)
		self.merged_df.plot(x='time',y='ard_val', color='red')
		plt.xlabel('time (s)')
		plt.ylabel('force (V)')
		plt.ylim(0, 5)
		# get start and end lines from merged data
		start_lines = []
		end_lines = []
		prev_state = self.merged_df['state'].iloc[0]
		for i, row in self.merged_df.iterrows():
			if row['state'] != prev_state:
				if row['state'][:4] == 'task':
					start_lines.append(row['time'])
				if prev_state[:4] == 'task':
					end_lines.append(row['time'])
			prev_state = row['state']

		for location in start_lines:
			plt.axvline(x=location)
		for location in end_lines:
			plt.axvline(x=location, color='green')
		plt.savefig(self.cur_time)


Experiment()

