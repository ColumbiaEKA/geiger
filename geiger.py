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
	print('\033[33m'+"[*] Reading configuration from {0}:".format(cmd_args.config)+'\033[39m')
	print('\033[32m'+"[+] Number of channels: {0}".format(num_channels)+'\033[39m')
	print('\033[32m'+"[+] Acquisition rate: {0}Hz".format(rate)+'\033[39m')
	print('\033[32m'+"[+] Frame buffer size: {0}".format(frames_per_buffer)+'\033[39m')

	#Ask user for length of recording
	try:
		recording_time = int(raw_input('\033[33m'+"\nEnter the recording time in seconds ({0}s) --> ".format(recording_time)+'\033[39m'))
	except ValueError:
		pass

	print('\033[32m'+"[+] Recording time set to {0}s".format(recording_time)+'\033[39m')

	#Ask user for which recording interface to use
	devices = Recorder.list_devices()
	print('\033[33m'+"\n[*] Select a recording device (0-{0}) among:\n".format(len(devices) - 1)+'\033[39m')
	for n,device in enumerate(devices):
		print('\033[33m'+"{0}: {1}".format(n,device)+'\033[39m')

	try:
		input_device_index = int(raw_input("-->"))
	except ValueError:
		input_device_index = 0

	print('\033[32m'+"[+] Selected device {0}: {1}\n".format(input_device_index,devices[input_device_index])+'\033[39m')

	#Set up the recorder instance
	recorder = Recorder(channels=num_channels,rate=rate,frames_per_buffer=frames_per_buffer,input_device_index=input_device_index)

	#Select the threshold and the slope type
	try:
		threshold = float(raw_input('\033[33m'+"[*] Select a threshold: "+'\033[39m'))
	except ValueError:
		threshold = 0.0

	print('\033[32m'+"[+] Threshold set to {0:.2e}\n".format(threshold)+'\033[39m')

	slope = raw_input('\033[33m'+"[*] Select a triggering slope (raising, descending): "+'\033[39m')
	if slope=="":
		slope = "raising"

	assert slope in ["raising","descending"],"slope must be either raising or descending!"
	print('\033[32m'+"[+] Slope set to {0}\n".format(slope)+'\033[39m')

	#Inform user if whole waveform will be saved
	if save_full_waveform:	
		
		print('\033[32m'+"[+] According to the configuration, you want to save the whole waveform"+'\033[39m')
		waveform_file = raw_input('\033[33m'+"[*] Select a file to write the whole waveform to: "+'\033[39m')
		print('\033[32m'+"[+] The full waveform will be saved to: {0}\n".format(waveform_file)+'\033[39m')


	#Start the recording
	t,y = recorder.record_above_threshold(seconds=recording_time,threshold=threshold,slope=slope,save_waveform=save_full_waveform)

	#Save positive events to txt file
	print('\033[33m'+"\n[*] Specify a file on which to save the events ({0}) ".format(options.get("output","events_file"))+'\033[39m')
	events_file = raw_input('\033[33m'+"-->"+'\033[39m')
	if events_file=="":
		events_file = options.get("output","events_file")

	print('\033[32m'+"[+] Saving events to {0}".format(events_file)+'\033[39m')
	np.savetxt(events_file,t)

	if save_full_waveform:
		
		print('\033[32m'+"[+] Saving full waveform (t,y) to {0}".format(waveform_file)+'\033[39m')
		np.save(waveform_file,np.array([recorder.time,recorder.signal]))
		answer = raw_input('\033[33m'+"[*] Do you want to plot the waveform? (y/n)"+'\033[39m')
		
		if answer in ["y","yes"]:
			
			recorder.visualize()
			recorder.ax.scatter(t,y,color="red")
			figure_file = waveform_file.split(".")[0]+".png"
			print('\033[33m'+"[+] Plotting waveform to {0}".format(figure_file)+'\033[39m')
			recorder.savefig(figure_file)


	#Quit
	print('\033[31m'+"[-] Event recording complete, bye"+'\033[39m')


if __name__=="__main__":
	main()