"""Read in oscilloscope signals through the sound card and select meaningful events"""
from __future__ import print_function,division

import numpy as np
import pyaudio

#Check if matplotlib is installed
try:
	import matplotlib.pyplot as plt
	matplotlib = True
except ImportError:
	matplotlib = False


#################################################
##########Recorder class#########################
#################################################

class Recorder(object):

	"""
	Class handler of a sound card recorder

	"""

	def __init__(self,channels=1,rate=44100,frames_per_buffer=1024):

		self.channels = channels
		self.rate = rate
		self.frames_per_buffer = frames_per_buffer

	def start(self):

		#Open the sound card and instantiate the stream object
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=pyaudio.paFloat32,channels=self.channels,rate=self.rate,input=True,frames_per_buffer=self.frames_per_buffer)

		#Log beginning of recordings to user
		print("[+] Started recording, channels={0}, rate={1}, frames per buffer={2}".format(self.channels,self.rate,self.frames_per_buffer))


	def record(self,seconds=5):

		#Start recording
		self.start()

		#Read the input from the card in chunks of fixed size for the amount of seconds specified in the input
		frames = list()

		for n in range(0,int(self.rate*seconds / self.frames_per_buffer)):
			frames.append(self.stream.read(self.frames_per_buffer))

		#Convert the stream into a numpy array
		self.signal = np.fromstring("".join(frames),dtype=np.float32) 
		self.time = np.linspace(0,seconds,self.signal.shape[0])

		#Stop recording
		self.stop()

		#Return time series to the user
		return self.time,self.signal


	def play(self,y=None):

		"""
		Play the recorded (or externally fed) sound
		"""
		
		print("[+] Play")
		
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=pyaudio.paFloat32,channels=self.channels,rate=self.rate,output=True)

		if y is not None:
			to_play = y
		else:
			to_play = self.signal

		self.stream.write(to_play.tostring())

		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

		print("[-] Stop")


	def visualize(self,fig=None,ax=None):

		"""
		Visualize the waveform

		"""

		if not matplotlib:
			raise ImportError("matplotlib is not installed, can't plot")

		#Instantiate figure
		if fig is None or ax is None:
			self.fig,self.ax = plt.subplots()
		else:
			self.fig = fig
			self.ax = ax

		#Plot the waveform
		self.ax.plot(self.time,self.signal)
		self.ax.set_xlabel(r"$t(\mathrm{s})$")
		self.ax.set_ylabel(r"$y(\mathrm{u.a.})$")


	def stop(self):

		#Stop recording and release the sound card
		print("[-] Stopped recording")
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()