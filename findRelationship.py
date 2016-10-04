import os
import nltk

class EpisodesSentences:

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
			text = episode_file.read()
			sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
			sentences = sentence_tokenizer.tokenize(text)
			episode_file.close()
			self.i += 1
			return sentences

class Relationships:

	def __init__(self, entities, sentences):
		self.relationships = []
		self._findRelationships(entities, sentences)

	def _findRelationships(self, entities, sentences):
		for sentence in sentences:
			self._findRelationshipsInSentence(sentence, entities)

	def _findRelationshipsInSentence(self, sentence, entities):
		tokens = nltk.word_tokenize(sentence)
		# pega os tokens que são entidades
		entities_of_sentence = self._getEntitiesOfSentence(tokens, entities)
		# aplica os pos_tag nos tokens da sentença
		tagging_tokens = nltk.pos_tag(tokens)

		if len(entities_of_sentence) > 1:
			# gera duplas de entidades seguidas na sentença
			for index in range(1,len(entities_of_sentence)):
				entities_double = (entities_double[index-1], entities_double[index])
				relationsship = self._getRelationship(entities_double, tokens)
				self.relationships.append(relationsship)

	def _getEntitiesOfSentence(self, tokens, entities):
		tokens_entities = []
		for index in range(len(tokens)):
			token = tokens[index]
			if token in entities.entities:
				tokens_entities.append((token, index)
		return tokens_entities

	def _getRelationship(entities_double, tokens_sentence):
		# identifica o verbo entre duas entidades.
		# gera uma tripla.
		# retorna a relação.
		pass

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i >= self.length:
			raise StopIteration
		else:
			relationship = self.relationships[self.i]
			self.i += 1
			return relationship
