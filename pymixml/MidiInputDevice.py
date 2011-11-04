from pymixml.InputDevice import *
import pypm

class MidiInputDevice(InputDevice):
	def __init__(self, midiDevice):
		super(MidiInputDevice, self).__init__()
		self.midi = midiDevice;

	def Terminate(self):
		del self.midi
		pypm.Terminate()
