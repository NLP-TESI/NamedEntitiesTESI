import os
import nltk
from functools import reduce

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

	def _findRelationships(self, entities, sentences_episodes):
		total = [ len(s) for s in sentences_episodes ]
		total = reduce(lambda x,y: x+y, total)
		count = 1
		for sentences_episode in sentences_episodes:
			for sentence in sentences_episode:
				self._findRelationshipsInSentence(sentence, entities)
				print("\r "+str(count)+" of "+str(total),end='')
				count += 1
		print('\r'+(' '*100)+'\n')

	def _findRelationshipsInSentence(self, sentence, entities):
		tokens = nltk.word_tokenize(sentence)
		# pega os tokens que são entidades
		entities_of_sentence = self._getEntitiesOfSentence(tokens, entities)
		# aplica os pos_tag nos tokens da sentença
		tagging_tokens = nltk.pos_tag(tokens)

		if len(entities_of_sentence) > 1:
			# gera duplas de entidades seguidas na sentença
			for index in range(1,len(entities_of_sentence)):
				entities_double = (entities_of_sentence[index-1], entities_of_sentence[index])
				relationsship = self._getRelationship(entities_double, tagging_tokens)
				if relationsship is not None:
					self.relationships.append(relationsship)

	def _getEntitiesOfSentence(self, tokens, entities):
		tokens_entities = []
		for index in range(len(tokens)):
			token = tokens[index]
			if token in entities:
				tokens_entities.append((token, index))
		return tokens_entities

	def _getRelationship(self, entities_double, tokens_sentence):
		start = entities_double[0][1]
		end = entities_double[1][1]+1
		relationship = None
		for index in range(start, end):
			if tokens_sentence[index][1] == 'VBZ':
				relationship = (entities_double[0], tokens_sentence[index], entities_double[1])
		return relationship

	def __len__(self):
		return len(self.relationships)

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
