"""Read in oscilloscope signals through the sound card and select meaningful events"""
from __future__ import print_function,division,with_statement

import numpy as np
import pyaudio
import wave

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

	def __init__(self,channels=1,rate=44100,frames_per_buffer=1024,input_device_index=None,output_device_index=None):

		self.channels = channels
		self.rate = rate
		self.frames_per_buffer = frames_per_buffer
		self.input_device_index = input_device_index
		self.output_device_index = output_device_index

	@classmethod
	def list_devices(cls):

		p = pyaudio.PyAudio()

		devices = list()
		for n in range(p.get_device_count()):
			devices.append(p.get_device_info_by_index(n)["name"])
		
		p.terminate()

		return devices

	def start(self):

		#Open the sound card and instantiate the stream object
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=pyaudio.paFloat32,channels=self.channels,rate=self.rate,input=True,frames_per_buffer=self.frames_per_buffer,input_device_index=self.input_device_index)

		#Get the name of the device
		try:
			device_name = self.p.get_device_info_by_index(self.input_device_index)["name"]
		except:
			device_name = self.p.get_default_input_device_info()["name"] 

		#Log beginning of recordings to user
		print("[+] Started recording on {0}, channels={1}, rate={2}, frames per buffer={3}".format(device_name,self.channels,self.rate,self.frames_per_buffer))


	def record(self,seconds=5,visualize=False):

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

		#Maybe visualize the waveform
		if visualize:
			self.visualize()

		#Return time series to the user
		return self.time,self.signal


	def record_above_threshold(self,seconds=10,threshold=0.5,save_waveform=False):

		"""
		Perform triggering in real time keeping only the events above threshold

		"""

		time_global = list()
		above_global = list()
		num_frames = int(self.rate*seconds / self.frames_per_buffer) 

		if save_waveform:
			all_frames = list()

		#Start recording
		self.start()

		for n in range(0,num_frames):
			
			#Read in the signal
			frame = np.fromstring(self.stream.read(self.frames_per_buffer),dtype=np.float32)

			if save_waveform:
				all_frames.append(frame)
			
			#Get the corresponding time
			time = np.linspace(n*seconds/num_frames,(n+1)*seconds/num_frames,len(frame))
			
			#Perform the selection
			above_current = np.where(frame>threshold)[0]
			time_global.append(time[above_current])
			above_global.append(frame[above_current])


		#Stop recording
		self.stop()

		if save_waveform:
			self.signal = np.concatenate(all_frames)
			self.time = np.linspace(0,seconds,self.signal.shape[0])

		#Log progress to user
		time_global = np.concatenate(time_global)
		above_global = np.concatenate(above_global)
		
		print("[+] Found {0} events above the threshold={1:.2e}".format(len(above_global),threshold))

		#Return
		return time_global,above_global


	def play(self,y=None):

		"""
		Play the recorded (or externally fed) sound
		"""

		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=pyaudio.paFloat32,channels=self.channels,rate=self.rate,output=True,output_device_index=self.output_device_index)

		#Get the name of the device
		try:
			device_name = self.p.get_device_info_by_index(self.output_device_index)["name"]
		except:
			device_name = self.p.get_default_output_device_info()["name"] 
		
		print("[+] Play on {0}".format(device_name))

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
		if hasattr(self,"fig") and hasattr(self,"ax"):
			pass
		else:
			
			if fig is None or ax is None:
				self.fig,self.ax = plt.subplots()
			else:
				self.fig = fig
				self.ax = ax

		#Plot the waveform
		if hasattr(self,"waveform"):
			self.waveform[0].set_xdata(self.time)
			self.waveform[0].set_ydata(self.signal)
			self.ax.set_xlim(self.time.min(),self.time.max())
			self.ax.set_ylim(self.signal.min(),self.signal.max())
		else:
			self.waveform = self.ax.plot(self.time,self.signal)
			self.ax.set_xlabel(r"$t(\mathrm{s})$")
			self.ax.set_ylabel(r"$y(\mathrm{u.a.})$")


	def stop(self):

		#Stop recording and release the sound card
		print("[-] Stopped recording")
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()


	@classmethod
	def load(cls,filename,**kwargs):

		t,y = np.load(filename)
		recorder = cls(**kwargs)

		setattr(recorder,"time",t)
		setattr(recorder,"signal",y)

		return recorder


	def save(self,filename):

		"""
		Save current recording to wave file

		"""

		#Parse the desired format from the filename
		extension = filename.split(".")[-1]

		print("[+] Saving waveform to {0}".format(filename))

		if extension=="npy":
		
			np.save(filename,np.array([self.time,self.signal]))

		else:
			p = pyaudio.PyAudio()

			wf = wave.open(filename,"wb")
			wf.setnchannels(self.channels)
			wf.setsampwidth(p.get_sample_size(pyaudio.paFloat32))
			wf.setframerate(self.rate)
			wf.writeframes(self.signal.tostring())
			wf.close()

			p.terminate()


	def savefig(self,filename):

		"""
		Saves current waveform to external image

		"""

		if not hasattr(self,"fig"):
			self.visualize()

		self.fig.savefig(filename)



