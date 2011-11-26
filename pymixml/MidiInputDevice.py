from pymixml.InputDevice import *
import pypm

_behringer_dict = {
	144 : {
		0 : ('rewind', 0),
		1 : ('forward', 0),
		2 : ('bend-', 0),
		3 : ('bend+', 0),
		6 : ('rewind', 1),
		7 : ('forward', 1),
		8 : ('bend-', 1),
		9 : ('bend+', 1),
		18 : ('play', 0),
		19 : ('cue', 0),
		26 : ('play', 1),
		27 : ('cue', 1),
	},
	176 : {
		0 : ('volume', 0),
		1 : ('crossfade', -1),
		2 : ('volume', 1),
		11 : ('pitch', 0),
		12 : ('pitch', 1),
		18 : ('search', 1),
		19 : ('search', 0),
	},
}

class MidiInputDevice(InputDevice):
	def __init__(self, midiDevice):
		super(MidiInputDevice, self).__init__()
		self.midi = midiDevice;

	def Terminate(self):
		del self.midi
		pypm.Terminate()

	def Read(self):
		while not self.midi.Poll(): pass
		MidiData = self.midi.Read(1)
		assert len(MidiData)==1
		assert len(MidiData[0])==2
		MidiData = MidiData[0][0]
		assert MidiData
		assert MidiData[3] == 0
		button = _behringer_dict[MidiData[0]][MidiData[1]]
		return (button[0], button[1], MidiData[2])

