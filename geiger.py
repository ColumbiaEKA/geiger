#!/usr/local/bin/python

from __future__ import with_statement
import ConfigParser,argparse
from counter import Recorder

import numpy as np

def main():

	#Parse configuration file from command line
	parser = argparse.ArgumentParser()
	parser.add_argument("-f","--file",dest="config",action="store",default="config",type=str,help="configuration file")
	cmd_args = parser.parse_args()

	#Read in the configuration file
	options = ConfigParser.ConfigParser()
	with open(cmd_args.config,"r") as configfile:
		options.readfp(configfile)

	num_channels = options.getint("counter","num_channels")
	rate = options.getint("counter","rate")
	frames_per_buffer = options.getint("counter","frames_per_buffer")
	recording_time = options.getfloat("counter","recording_time")
	save_full_waveform = options.getboolean("output","save_full_waveform")

	#Print default recording info
	print("[*] Reading configuration from {0}:".format(cmd_args.config))
	print("[+] Number of channels: {0}".format(num_channels))
	print("[+] Acquisition rate: {0}Hz".format(rate))
	print("[+] Frame buffer size: {0}".format(frames_per_buffer))

	#Ask user for length of recording
	try:
		recording_time = int(raw_input("\nEnter the recording time in seconds ({0}s) --> ".format(recording_time)))
	except:
		pass

	print("[+] Recording time set to {0}s".format(recording_time))

	#Ask user for which recording interface to use
	devices = Recorder.list_devices()
	print("\n[*] Select a recording device (0-{0}) among:\n".format(len(devices) - 1))
	for n,device in enumerate(devices):
		print("{0}: {1}".format(n,device))

	try:
		input_device_index = int(raw_input("-->"))
	except:
		input_device_index = 0

	print("[+] Selected device {0}: {1}\n".format(input_device_index,devices[input_device_index]))

	#Set up the recorder instance
	recorder = Recorder(channels=num_channels,rate=rate,frames_per_buffer=frames_per_buffer,input_device_index=input_device_index)

	#Select the threshold and the slope type
	try:
		threshold = float(raw_input("[*] Select a threshold: "))
	except:
		threshold = 0.0

	print("[+] Threshold set to {0:.2e}\n".format(threshold))

	slope = raw_input("[*] Select a triggering slope (raising, descending): ")
	if slope=="":
		slope = "raising"

	assert slope in ["raising","descending"],"slope must be either raising or descending!"
	print("[+] Slope set to {0}\n".format(slope))

	#Inform user if whole waveform will be saved
	if save_full_waveform:	
		
		print("[+] According to the configuration, you want to save the whole waveform")
		waveform_file = raw_input("[*] Select a file to write the whole waveform to: ")
		print("[+] The full waveform will be saved to: {0}\n".format(waveform_file))


	#Start the recording
	t,y = recorder.record_above_threshold(seconds=recording_time,threshold=threshold,slope=slope,save_waveform=save_full_waveform)

	#Save positive events to txt file
	print("\n[*] Specify a file on which to save the events ({0}) ".format(options.get("output","events_file")))
	events_file = raw_input("-->")
	if events_file=="":
		events_file = options.get("output","events_file")

	print("[+] Saving events to {0}".format(events_file))
	np.savetxt(events_file,t)

	if save_full_waveform:
		print("[+] Saving full waveform (t,y) to {0}".format(waveform_file))
		np.save(waveform_file,np.array([recorder.time,recorder.signal]))


	#Quit
	print("[-] Event recording complete, bye")


if __name__=="__main__":
	main()