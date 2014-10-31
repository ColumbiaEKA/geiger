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

#Set the threshold
threshold = float(raw_input("select a threshold --> "))

#Set the slope
slope = raw_input("select the slope (raising,descending) --> ")
if slope not in ["raising","descending"]:
	slope = "raising"

print("[+] Proceeding with {0} slope".format(slope))

recorder = Recorder(input_device_index=input_device_index)
t,y = recorder.record_above_threshold(seconds=5,threshold=threshold,save_waveform=True)

#Visualize waveform and events above threshold
recorder.visualize()
recorder.ax.scatter(t,y,color="red")
recorder.ax.set_title("{0} events above the threshold {1:.2e}".format(len(t),threshold))
recorder.savefig("above_threshold.png")