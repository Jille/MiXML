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
		return ''.join(self.text)

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

if __name__ == '__main__':
	mf = MiXMLFile()
	mf.load('../example.xml')
	print mf.decks
	print mf.transitions
