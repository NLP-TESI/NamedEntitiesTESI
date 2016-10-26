import os
import nltk
from Util import TESIUtil	
from NamedEntities.NamedEntity import NamedEntity

NOT_AN_ENTITY = ['–', '–', '—', '[', '', 'imp', 'beyond', 'house', 'ser ser']

class EpisodeFile:
	def __init__(self, path, season, ep_number):
		self._path = path
		self._season = season.replace('season_', '')
		self._ep_number = ep_number

		file_deaths = open(os.path.join(path, 'deaths.txt'))
		self._deaths = file_deaths.read()
		file_deaths.close()

		file_ep_name = open(os.path.join(path, 'ep_name.txt'))
		self._title = file_ep_name.read()
		file_ep_name.close()

		file_text = open(os.path.join(path, 'clean_text.txt'))
		self._text = file_text.read()
		file_text.close()

		if(os.path.isfile(os.path.join(path, 'tagged_text.txt'))):
			file_tagged_text = open(os.path.join(path, 'tagged_text.txt'))
			self._tagged_text = file_tagged_text.read()
			file_tagged_text.close()

	def path(self):
		return self._path

	def season(self):
		return int(self._season)

	def number(self):
		return int(self._ep_number)

	def text(self):
		return self._text

	def tagged_text(self):
		return self._tagged_text

	def save_tfidf(self, tfidf):
		string = ""

		for t in tfidf:
			string += t + ";" + str(tfidf[t]) + "\n"

		file_tfidf = open(os.path.join(self._path, 'tfidf.csv'), 'w')
		file_tfidf.write(string)
		file_tfidf.close()


	def markup_entities(self, global_entities_dic):
		return self._mark_named_entities(global_entities_dic)

	def _mark_named_entities(self, global_entities_dic):
		sentences = nltk.sent_tokenize(self._text)
		sentences = list(filter(('\n').__ne__, sentences))

		local_entities = {}
		taggeds = []
		for index, sentence in enumerate(sentences):
			sentence_id = str(self._season) + str(self._ep_number) + str(index)
			result_tagged, entities = self._analyze_sentence_with_chunk(sentence, sentence_id)
			taggeds.append(result_tagged)
			
			for key in entities:
				e = entities[key]
				term = list(e.terms().keys())[0]
				if term in local_entities:
					local_entities[term].add_entity(e)
				else:
					local_entities[term] = e

		global_entities_dic = self._find_similar_entities(global_entities_dic, local_entities)

		return (taggeds, global_entities_dic)

	def _find_similar_entities(self, global_entities_dic, local_entities_dic):
		final_dict = global_entities_dic

		for key1 in local_entities_dic:
			item1 = local_entities_dic[key1]

			term1 = list(item1.terms().keys())[0]
			str1 = TESIUtil.remove_honor_words(list(item1.terms().keys())[0])

			betters = []

			for key2 in final_dict:
				item2 = final_dict[key2]
				sum_sim = 0
				qty = 0

				if(term1 in item2.terms()):
					betters.append(item2)
				else:
					for term2 in item2.terms():
						str2 = TESIUtil.remove_honor_words(term2)
						sum_sim += TESIUtil.string_similarity(str1, str2)
						qty += 1
					avg = sum_sim/qty
					if(avg > 0.7):
						betters.append(item2)
			
			betters.sort(key=lambda item: item.frequency())

			if(len(betters) == 0):
				final_dict[item1.id()] = item1
			else:
				choosed = None
				for candidate in betters:
					if(choosed is None or 
					  (choosed is not None and choosed.frequency() < candidate.frequency())):
						choosed = candidate

				if(choosed == None):
					choosed = betters[0]

				final_dict[item1.id()] = choosed
				choosed.add_entity(item1)

		return final_dict

	def _add_in_entities_dictionary(self, dic, string, index):
		if(string in dic):
			e = dic[string]
			e.add_name(string, index)
		else:
			e = NamedEntity(name=string, last=index)
			dic[string] = e
		return e

	def _analyze_sentence_with_chunk(self, sentence, index):
		tokenized = nltk.word_tokenize(sentence)
		tagging = nltk.pos_tag(tokenized)
		chunked = nltk.ne_chunk(tagging)

		i = 0
		result = []
		dic_entities = {}

		while i < len(chunked):
			if(type(chunked[i]) is nltk.tree.Tree):
				if(chunked[i][0][0].lower() == 'house'):
					type_ne = 'HSE'
				else:
					type_ne = 'NE'

				string = ''
				for s in chunked[i]:
					string += ' ' + s[0]
				stop = False

				while(i+1 < len(chunked) and not stop):
					stop = True
					if(type(chunked[i+1]) is nltk.tree.Tree):
						stop = False
						for s in chunked[i]:
							string += ' ' + s[0]
					
					elif(chunked[i+1][1] == 'NNP'):
						stop = False
						string += ' ' + chunked[i+1][0]
					else:
						i -= 1
					i += 1

				# Special case to: Night's Watch
				if(i+2 < len(chunked) and type(chunked[i+1]) is not nltk.tree.Tree and
					chunked[i+1][0] == "'s" and type(chunked[i+2]) is nltk.tree.Tree
					and chunked[i+2][0][0].lower() == 'watch'):
					string += chunked[i+1][0] + ' ' + chunked[i+2][0][0]
					i += 2

				string = string.strip()
				
				if(string.lower() in NOT_AN_ENTITY):
					item = (string, 'SYM')
				else:
					e = self._add_in_entities_dictionary(dic_entities, string, index)
					item = (string, type_ne, e.id())
				
				result.append(item)
			else:
				item = chunked[i]
				result.append(item)

			i += 1

		return (result, dic_entities)

class FileSet:
	def __init__(self, dirname):
		self._episodes = []

		for season in os.listdir(dirname):
			if('.csv' in season):
					continue
			for ep in os.listdir(os.path.join(dirname, season)):
				episode = EpisodeFile(os.path.join(dirname, season, ep), season, ep)
				self._episodes.append(episode)

		self._episodes = self._sort_by_season_and_episode(self._episodes)
		

	def _sort_by_season_and_episode(self, lst):
		n = len(lst)
		i = n-1

		while i >= 1:
			j = 0
			while j < i:
				if(lst[j].season() > lst[j+1].season() or 
					(lst[j].season() == lst[j+1].season() and lst[j].number() > lst[j+1].number())):
					temp = lst[j]
					lst[j] = lst[j+1]
					lst[j+1] = temp
				j += 1
			i -= 1
		return lst

	def __len__(self):
		return len(self._episodes)

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i >= len(self._episodes):
			raise StopIteration
		else:
			self.i += 1
			return self._episodes[self.i-1]
	def __delitem__(self, key):
		del self._episodes[key]

	def __getitem__(self, key):
		return self._episodes[key]

	def __setitem__(self, key, value):
		self._episodes[key] = value
