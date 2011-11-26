from time import sleep

import gobject
gobject.threads_init() 

import pygst
pygst.require('0.10')
import gst

mainloop = gobject.MainLoop()

# gst-launch filesrc location=henk.mp3 ! decodebin ! audioconvert ! equalizer-3bands band0=12.0 ! alsasink

pipeline = gst.Pipeline('audiocontroller')
src = gst.element_factory_make('filesrc')
# src = gst.element_factory_make('audiotestsrc')
dec = gst.element_factory_make('decodebin')
conv = gst.element_factory_make('audioconvert')
eq = gst.element_factory_make('equalizer-3bands')
sink = gst.element_factory_make('autoaudiosink')

src.set_property('location', 'henk.mp3')
# src.set_property('freq', 300.0)
# src.set_property('volume', 1.0)

pipeline.add(src, dec, conv, eq, sink)

convsink = conv.get_pad('sink')

def link_dec_conv(element, pad, last):
	caps = pad.get_caps()
	name = caps[0].get_name()
	print '\n__on_new_decoded_pad:', name
	if 'audio' in name:
		if not convsink.is_linked(): # Only link once
			pad.link(convsink)

dec.connect('new-decoded-pad', link_dec_conv)

src.link(dec)
conv.link(eq)
eq.link(sink)

control = gst.Controller(eq, 'band0', 'band1', 'band2')
control.set_interpolation_mode('band0', gst.INTERPOLATE_NONE)
control.set_interpolation_mode('band1', gst.INTERPOLATE_NONE)
control.set_interpolation_mode('band2', gst.INTERPOLATE_NONE)
# control.set("band0", 4 * gst.SECOND, 12)
if True:
	res = control.set("band1", 0, 12.0)
	assert res
	res = control.set("band1", 4 * gst.SECOND, -12.0)
	assert res
	res = control.set("band1", 8 * gst.SECOND, 12.0)
	assert res
	res = control.set("band1", 12 * gst.SECOND, -12.0)
	assert res
	# control.set("band0", 12 * gst.SECOND, 0)

# sc = gst.Controller(src, 'volume')
# sc.set_interpolation_mode('volume', gst.INTERPOLATE_LINEAR)

res_ = pipeline.set_state(gst.STATE_PLAYING)
if res_ == gst.STATE_CHANGE_ASYNC:
	res_ = pipeline.get_state()[0]
if res_ != gst.STATE_CHANGE_SUCCESS:
	print "Could not set pipeline %s to PLAYING" % pipeline
	print res_
# eq.set_property('band2', 12.0)

try:
	for i in xrange(0, 20):
		print i
		if False:
			if i % 2 == 1:
				print "Whop"
				eq.set_property('band0', -12.0)
			else:
				print "Plop"
				eq.set_property('band0', 12.0)
		sleep(1)
	print eq
	mainloop.run()
except KeyboardInterrupt:
	pass

res = pipeline.set_state(gst.STATE_NULL)
if res != gst.STATE_CHANGE_SUCCESS:
	print "Could not set pipeline %s to NULL" % pipeline
	exit(1)
