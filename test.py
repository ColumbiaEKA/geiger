from counter import Recorder

try:
	input_device_index = int(raw_input("Specify input device index (default 0) --> "))
except ValueError:
	input_device_index = None


recorder = Recorder(input_device_index=input_device_index)
recorder.record(5)
recorder.play()

try:
	recorder.savefig("waveform.png")
	print("[+] Saving waveform to waveform.png")
except:
	pass