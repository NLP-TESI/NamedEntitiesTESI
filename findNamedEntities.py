import os
import nltk

class EpisodesFiles:

	def __init__(self, dirname):
		self.seasons = []
		for season in os.listdir(dirname):
			self.seasons += [os.path.join(dirname,os.path.join(season,x)) for x in os.listdir(os.path.join(dirname,season))]
		
		self.length = len(self.seasons)

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i >= self.length:
			raise StopIteration
		else:
			episode_file = open(self.seasons[self.i])
			text = episode_file.readlines()
			episode_file.close()
			self.i += 1
			return text

class NamedEntitiesSetence:

	def __init__(self, sentence):
		self.sentence = sentence

	def _isFinalEntity(self, name):
		if(name[0].isupper()):
			prev_lower = False

			for l in name[1:]:
				upper = l.isupper()
				if(prev_lower and upper):
					return False or ("MC" in name.upper())

				prev_lower = l.islower()
		else:
			return False
		return True

	def _analizeTree(self, parent, entities):
		for node in parent:
			if type(node) is nltk.Tree:
				self._analizeTree(node, entities)

		label = parent.label()
		if(label == 'GPE' or label == 'PERSON' or label == 'ORGANIZATION'):
			name = ""
			for leaf in parent.leaves():
				name += " " + leaf[0]
			name = name.strip()

			if(self._isFinalEntity(name)):
				entities[name] = label
			#else:
			#	print(name)

	def getEntities(self):
		entities = {}

		tokenized = nltk.word_tokenize(self.sentence)
		tagging = nltk.pos_tag(tokenized)
		result = nltk.ne_chunk(tagging)

		self._analizeTree(result, entities)

		return entities

class NamedEntities:
	
	def __init__(self, episodes):
		self.entities = self._getNamedEntities(episodes)
	
	def __len__(self):
		return len(self.entities)

	def _getNamedEntities(self,episodes):
		entities = {}
		for episode in episodes:
			for line in episode:
				if len(line) > 1:
					entities.update(NamedEntitiesSetence(line).getEntities())

		entitiesList = [ key for key in entities ]
		return entitiesList


	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i >= len(self.entities):
			raise StopIteration
		else:
			self.i += 1
			return self.entities[self.i-1]


