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
			text = episode_file.read()
			episode_file.close()
			self.i += 1
			return text
