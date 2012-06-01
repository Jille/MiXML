from time import sleep, time

import gobject
gobject.threads_init() 

import pygst
pygst.require('0.10')
import gst

from xmlhandler import MiXMLFile

def gst_set_state_synchr(el, state):
	res_ = el.set_state(state)
	if res_ == gst.STATE_CHANGE_ASYNC:
		res_ = el.get_state()[0]
	if res_ != gst.STATE_CHANGE_SUCCESS:
		print "Could not set %s's state to %s" % (el, state)
		print res_

class InputBin:
	def __init__(self, srctype):
		self.bin = gst.Bin()
		self.src = gst.element_factory_make(srctype)
		self.dec = gst.element_factory_make('decodebin')
		self.conv = gst.element_factory_make('audioconvert')
		self.speed = gst.element_factory_make('speed')
		self.eq = gst.element_factory_make('equalizer-3bands')
		self.vol = gst.element_factory_make('volume')
		self.bin.add(self.src, self.dec, self.speed, self.conv, self.eq, self.vol)

		self.dec.connect('new-decoded-pad', self.__link_dec_conv)
		self.src.link(self.dec)
		self.speed.link(self.conv)
		self.conv.link(self.eq)
		self.eq.link(self.vol)

		self.ghost_pad = gst.GhostPad('src', self.vol.get_pad('src'))
		self.bin.add_pad(self.ghost_pad)

	def __link_dec_conv(self, element, pad, last):
		spad = self.speed.get_pad('sink')
		caps = pad.get_caps()
		name = caps[0].get_name()
		print '\n__link_dec_conv:', name
		if 'audio' in name:
			if not spad.is_linked(): # Only link once
				pad.link(spad)

	def set_state(self, state):
		gst_set_state_synchr(self.bin, state)

	def add_to_pipeline(self, pipeline, adder):
		self.sinkpad = adder.get_request_pad("sink%d")
		pipeline.add(self.bin)
		self.ghost_pad.link(self.sinkpad)
		self.set_state(pipeline.get_state()[1])

	def remove_from_pipeline(self, pipeline, adder):
		self.ghost_pad.set_blocked(True)
		self.bin.set_state(gst.STATE_NULL)
		self.ghost_pad.unlink(self.sinkpad)
		adder.release_request_pad(self.sinkpad)
		pipeline.remove(self.bin)

mainloop = gobject.MainLoop()
pipeline = gst.Pipeline()
adder = gst.element_factory_make('adder')
sink = gst.element_factory_make('autoaudiosink')
pipeline.add(adder, sink)
adder.link(sink)

decks = {}
anyPlaying = False

mf = MiXMLFile()
mf.load('crygroove.xml')

for dname, deck in mf.decks.items():
	decks[dname] = InputBin('filesrc')
	decks[dname].src.set_property('location', deck['sha1'] +'.mp3')
	if deck['initialState']['playing']:
		decks[dname].add_to_pipeline(pipeline, adder)
		anyPlaying = True

if anyPlaying:
	print "Starting full pipeline..."
	gst_set_state_synchr(pipeline, gst.STATE_PLAYING)
	print " OK"

nul = time()

print "Running"

try:
	while len(mf.transitions) > 0:
		tr = mf.transitions.pop(0)
		deck = decks[tr['deck']]
		now = (time() - nul) * 1000000
		if now < tr['ts']:
			print "Waiting %f for %s" % ((tr['ts'] - now) / 1000000, tr['type'])
			sleep((tr['ts'] - now) / 1000000)
		else:
			print "Going for %s" % tr['type']
		if tr['type'] == 'start':
			deck.add_to_pipeline(pipeline, adder)
			if not anyPlaying:
				print "Starting full pipeline..."
				gst_set_state_synchr(pipeline, gst.STATE_PLAYING)
				print " OK"
				anyPlaying = True
		elif tr['type'] == 'stop':
			deck.remove_from_pipeline(pipeline, adder)
		elif tr['type'] == 'jump':
			deck.bin.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, tr['value'] * 1000)
			# deck.bin.seek(1.0, gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, 45, gst.SEEK_TYPE_NONE, 30)
			# deck.bin.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, 45 * gst.SECOND)
			# pipeline.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, tr['value'] * 1000)
			print float(tr['value']) / 1000000.0
		elif tr['type'] == 'pitch':
			deck.speed.set_property('speed', 1 + (float(tr['value']) / 100))
			print 1 + (float(tr['value']) / 100)
		elif tr['type'] == 'volume':
			deck.vol.set_property('volume', float(tr['value']) / 100)
		else:
			print "%s is unsupported" % tr['type'] 
	print "Done with transitions"
	# print pipeline.query_position(gst.FORMAT_TIME, None)
	mainloop.run()
except KeyboardInterrupt:
	pass

res = pipeline.set_state(gst.STATE_NULL)
if res != gst.STATE_CHANGE_SUCCESS:
	print "Could not set pipeline %s to NULL" % pipeline
	exit(1)
