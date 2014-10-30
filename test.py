from counter import Recorder

recorder = Recorder()
recorder.record(5)
recorder.play()
recorder.save("output.wav")