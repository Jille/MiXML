from pymixml.OutputDevice import *
import pypm

_behringer_reverse_dict = {
	-1 : {
		'crossfade' : (176, 1),
	},
	0 : {
		'play' : (144, 18),
		'cue' : (144, 19),
		'rewind' : (144, 0),
		'forward' : (144, 1),
		'bend-' : (144, 2),
		'bend+' : (144, 3),
		'volume' : (176, 0),
		'pitch' : (176, 11),
		'search' : (176, 19),
	},
	1 : {
		'play' : (144, 26),
		'cue' : (144, 27),
		'rewind' : (144, 6),
		'forward' : (144, 7),
		'bend-' : (144, 8),
		'bend+' : (144, 9),
		'volume' : (176, 2),
		'pitch' : (176, 12),
		'search' : (176, 18),
	},
}

class MidiOutputDevice(OutputDevice):
	def __init__(self, midiDevice):
		super(MidiOutputDevice, self).__init__()
		self.midi = midiDevice;

	def Terminate(self):
		del self.midi
		pypm.Terminate()

	def Write(self, action, strength):
		button = _behringer_reverse_dict[action[1]][action[0]]
		print [[[button[0], button[1], strength], pypm.Time()]]
		self.midi.Write([[[button[0], button[1], strength], pypm.Time()]])
