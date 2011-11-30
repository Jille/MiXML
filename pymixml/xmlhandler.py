from xml.dom import minidom

class MiXMLNode:
	def __init__(self, node):
		self.attributes = dict()
		self.children_dict = dict()
		self.children_list = list()
		self.text = list()
		self.nodeName = node.nodeName

		for attr in dict(node.attributes):
			self.attributes[attr] = node.attributes[attr].value
		for child in node.childNodes:
			if child.nodeType == child.ELEMENT_NODE:
				sn = MiXMLNode(child)
				if child.nodeName not in self.children_dict:
					self.children_dict[child.nodeName] = list()
				self.children_dict[child.nodeName].append(sn)
				self.children_list.append(sn)
			elif child.nodeType == child.TEXT_NODE:
				self.text.append(child.nodeValue)

	def __getitem__(self, key):
		return self.children_dict[key]

	@property
	def fulltext(self):
		return ''.join(self.text).strip()

class MiXMLFile:
	def __init__(self):
		self.decks = {}
		self.transitions = []

	def load(self, file):
		tree = minidom.parse(file)
		root = MiXMLNode(tree.firstChild)
		for deckNode in root['mix'][0]['decks'][0]['deck']:
			d = {}
			d['grabAt'] = int(deckNode.attributes['grabAt'])
			if 'releaseAt' in deckNode.attributes:
				d['releaseAt'] = int(deckNode.attributes['releaseAt'])
			d['sha1'] = deckNode['sha1'][0].fulltext
			d['artist'] = deckNode['artist'][0].fulltext
			d['title'] = deckNode['title'][0].fulltext
			d['length'] = int(deckNode['length'][0].fulltext)
			d['initialState'] = {}
			d['initialState']['playing'] = deckNode['initialState'][0]['playing'][0].fulltext == 'true'
			self.decks[deckNode.attributes['name']] = d
		for trNode in root['mix'][0]['transitions'][0].children_list:
			print trNode.attributes
			t = {}
			t['type'] = trNode.nodeName
			t['ts'] = trNode.attributes['ts']
			t['deck'] = trNode.attributes['deck']
			if trNode.nodeName == 'volume':
				if 'stretch' in trNode.attributes:
					t['stretch'] = trNode.attributes['stretch']
				t['value'] = int(trNode.fulltext)
			elif trNode.nodeName == 'equalizer':
				t['channel'] = trNode.attributes['channel']
				if 'stretch' in trNode.attributes:
					t['stretch'] = trNode.attributes['stretch']
				t['value'] = int(trNode.fulltext)
			elif trNode.nodeName == 'jump':
				t['value'] = int(trNode.fulltext)
			elif trNode.nodeName in ('start', 'stop'):
				pass
			self.transitions.append(t)

	def save(self, fname):
		document = minidom.getDOMImplementation().createDocument(None, None, None)
		mixml = document.createElement('mixml')
		mixml.setAttribute("version", "0.1")
		mix = document.createElement('mix')
		decks = document.createElement('decks')
		for d, di in self.decks.items():
			deck = document.createElement('deck')
			deck.setAttribute("name", d)
			deck.setAttribute("grabAt", str(di['grabAt']))
			self._createNodeWithValue(document, deck, 'sha1', di['sha1'])
			self._createNodeWithValue(document, deck, 'artist', di['artist'])
			self._createNodeWithValue(document, deck, 'title', di['title'])
			self._createNodeWithValue(document, deck, 'length', str(di['length']))
			initialState = document.createElement('initialState')
			self._createNodeWithValue(document, initialState, 'playing', 'true' if di['initialState']['playing'] else 'false')
			deck.appendChild(initialState)
			decks.appendChild(deck)
		mix.appendChild(decks)
		transitions = document.createElement('transitions')
		for t in self.transitions:
			tr = document.createElement(t['type'])
			del t['type']
			if 'value' in t:
				tr.appendChild(document.createTextNode(str(t['value'])))
				del t['value']
			for k, v in t.items():
				tr.setAttribute(k, str(v))
			transitions.appendChild(tr)
		mix.appendChild(transitions)
		mixml.appendChild(mix)
		document.appendChild(mixml)
		with open(fname, 'w') as fh:
			fh.write(document.toprettyxml())

	def _createNodeWithValue(self, document, parent, tag, value):
		node = document.createElement(tag)
		node.appendChild(document.createTextNode(value))
		parent.appendChild(node)

if __name__ == '__main__':
	mf = MiXMLFile()
	mf.load('../example.xml')
	print mf.decks
	print mf.transitions
	mf.save('testout.xml')
