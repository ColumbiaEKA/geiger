from counter import Recorder

#log devices to user
print("Available audio devices:\n")

devices = Recorder.list_devices()
for n,device in enumerate(devices):
	print("{0}: {1}".format(n,device)) 

print("")

try:
	input_device_index = int(raw_input("Specify input device index (default 0) --> "))
except ValueError:
	input_device_index = None


recorder = Recorder(input_device_index=input_device_index)
recorder.record(5)
recorder.play()

recorder.save("waveform.npy")

try:
	recorder.savefig("waveform.png")
	print("[+] Saving waveform image to waveform.png")
except:
	pass