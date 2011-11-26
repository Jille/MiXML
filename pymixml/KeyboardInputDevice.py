from pymixml.InputDevice import *

_keyboard_dict = {
	'q' : ('cue', 0),
	'w' : ('play', 0),
	'e' : ('rewind', 0),
	'r' : ('forward', 0),
	't' : ('rewind', 0),
	'y' : ('forward', 0),

	'a' : ('cue', 1),
	's' : ('play', 1),
	'd' : ('rewind', 1),
	'f' : ('forward', 1),
	'g' : ('rewind', 1),
	'h' : ('forward', 1),

	'Q' : ('quit', -1),
}


class KeyboardInputDevice(InputDevice):
	def __init__(self):
		super(KeyboardInputDevice, self).__init__()
		try:
			self.readone = _GetchUnix()
		except ImportError:
			self.readone = _GetchWindows()

	def Read(self):
		rawbutton = self.readone()
		return _keyboard_dict[rawbutton]

# Source: http://code.activestate.com/recipes/134892/
class _GetchUnix:
	def __init__(self):
		import tty, sys

	def __call__(self):
		import sys, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(fd)
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

class _GetchWindows:
	def __init__(self):
		import msvcrt

	def __call__(self):
		import msvcrt
		return msvcrt.getch()
