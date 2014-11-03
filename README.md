Geiger counter
=============================

Read geiger counter voltages through the sound card of a computer and convert them into numpy arrays for further analysis. Makes use of the [pyaudio](http://people.csail.mit.edu/hubert/pyaudio) interface 

How it works
------------

To perform a digital recording from the geiger counter, just run the script from the command line

	./geiger.py

Additionally you can specify a custom configuration file which has some tunable options

	./geiger.py -f config

Interactive demo
----------------

[click here](http://nbviewer.ipython.org/github/apetri/Notebooks/blob/master/geiger_counter.ipynb)