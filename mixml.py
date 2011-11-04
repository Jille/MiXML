#!/usr/bin/env python

# MiXML, eternalized mixes in XML format
# Copyright Sjors Gielen, Jille Timmermans, 2011
#
# Parts of this file are from PyPortMidi by John Harrison

from pymixml.InputDevice import *
from pymixml.KeyboardInputDevice import *
from pymixml.MidiInputDevice import *
import pypm
import array
import time

def main():
	input=inputType()
	"""
    print "Midi Input opened. Reading ",NUM_MSGS," Midi messages..."
#    MidiIn.SetFilter(pypm.FILT_ACTIVE | pypm.FILT_CLOCK)
    for cntr in range(1,NUM_MSGS+1):
        while not MidiIn.Poll(): pass
        MidiData = MidiIn.Read(1) # read only 1 message at a time
        print "Got message ",cntr,": time ",MidiData[0][1],", ",
        print  MidiData[0][0][0]," ",MidiData[0][0][1]," ",MidiData[0][0][2], MidiData[0][0][3]
        # NOTE: most Midi messages are 1-3 bytes, but the 4 byte is returned for use with SysEx messages.
"""

	if isinstance(input, MidiInputDevice):
		input.Terminate()

def inputType():
	choice=0
	while (choice<1) or (choice>2):
		print """
Wat gaan we vandaag doen?

1) Lezen van MIDI
2) Lezen van toetsenbord
"""
		x=int(raw_input())
		if x == 1:
			return inputMidiType()
		elif x == 2:
			return KeyboardInputDevice()

def PrintDevices():
	for loop in range(pypm.CountDevices()):
		interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)

		if inp == 1:
			print loop, name," ",
			if (opened == 1): print "(opened)"
			else: print "(unopened)"
	print

def inputMidiType():
	pypm.Initialize()
	PrintDevices()
	dev = int(raw_input("Type input number: "))
	MidiIn = pypm.Input(dev)
	return MidiInputDevice(MidiIn)

main()
