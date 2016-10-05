import os
import TESIUtil
import nltk

class GOTFiles:
	def __init__(self, dirname):
		self.episodes = []

		for season in os.listdir(dirname):
			for ep in os.listdir(os.path.join(dirname, season)):
				episode = Episode(os.path.join(dirname, season, ep), season, ep)
				self.episodes.append(episode)

	def __len__(self):
		return len(self.episodes)

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i >= len(self.episodes):
			raise StopIteration
		else:
			self.i += 1
			return self.episodes[self.i-1]


class Episode:

	def __init__(self, path, season, ep_number):
		self._path = path
		self._season = season.replace('season_', '')
		self._ep_number = ep_number
		self._entities = []

		file_deaths = open(os.path.join(path, 'deaths.txt'))
		self._deaths = file_deaths.read()
		file_deaths.close()

		file_ep_name = open(os.path.join(path, 'ep_name.txt'))
		self._title = file_ep_name.read()
		file_ep_name.close()


		file_text = open(os.path.join(path, 'clean_text.txt'))
		self._text = file_text.read()
		file_text.close()

		if(not os.path.isfile(os.path.join(path, 'entities.txt'))):
			file_entities = open(os.path.join(path, 'entities.txt'), 'w')
			file_entities.write('\n'.join(sorted(self.get_named_entities())))
			file_entities.close()

		file_entities = open(os.path.join(path, 'entities.txt'))
		self._entities = sorted(file_entities.read().split('\n'))
		file_entities.close()

	def path(self):
		return self._path

	def get_named_entities(self):
		if(len(self._entities) == 0):
			self._extract_named_entities()
		return self._entities

	def _extract_named_entities(self):
		sentences = nltk.sent_tokenize(self._text)
		sentences = list(filter(('\n').__ne__, sentences))

		entities = {}
		for sentence in sentences:
			self._analize_sentence(sentence, entities)
		
		self._entities = entities

	def _analize_sentence(self, sentence, entities):
		tokenized = nltk.word_tokenize(sentence)
		tagging = nltk.pos_tag(tokenized)
		result_chunk = nltk.ne_chunk(tagging)

		self._analize_tree(result_chunk, entities)

		return entities

	def _analize_tree(self, parent, entities):
		for node in parent:
			if type(node) is nltk.Tree:
				self._analize_tree(node, entities)

		label = parent.label()
		if(label == 'GPE' or label == 'PERSON' or label == 'ORGANIZATION'):
			name = ""
			for leaf in parent.leaves():
				name += " " + leaf[0]
			name = name.strip()
			entities[name] = label