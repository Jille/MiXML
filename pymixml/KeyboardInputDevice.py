from pymixml.InputDevice import *

class KeyboardInputDevice(InputDevice):
	def __init__(self):
		super(KeyboardInputDevice, self).__init__()
		try:
			self.readone = _GetchUnix()
		except ImportError:
			self.readone = _GetchWindows()

	def Read(self):
		return self.readone()

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
