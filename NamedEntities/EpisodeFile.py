import os
import nltk
from Util import TESIUtil	
from NamedEntities.NamedEntity import NamedEntity

NOT_AN_ENTITY = ['–', '–', '—', '[', '', 'imp', 'beyond', 'house']

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

	def path(self):
		return self._path

	def season(self):
		return int(self._season)

	def number(self):
		return int(self._ep_number)

	def markup_entities(self, global_entities_dic):
		return self._mark_named_entities(global_entities_dic)

	def _mark_named_entities(self, global_entities_dic):
		sentences = nltk.sent_tokenize(self._text)
		sentences = list(filter(('\n').__ne__, sentences))

		taggeds = []
		entity_dic = {}
		for sentence in sentences:
			result_tagged, entities = self._analyze_sentence_with_chunk(sentence)
			taggeds.extend(result_tagged)
			entity_dic.update(entities)

		entity_list = TESIUtil.dict_to_list(entity_dic)
		merged_entities = self._find_similar_entities(entity_list, global_entities_dic)

		return (taggeds, merged_entities)

	def _find_similar_entities(self, entity_list, global_entities_dic):
		final_dict = global_entities_dic

		for item1 in entity_list:
			term1 = list(item1.terms().keys())[0]
			str1 = TESIUtil.remove_honor_words(list(item1.terms().keys())[0])

			best = None
			best_avg = 0

			for key2 in final_dict:
				item2 = final_dict[key2]
				sum_sim = 0
				qty = 0

				if(term1 in item2.terms()):
					best = item2
					best_avg = 1
					break

				for term2 in item2.terms():
					str2 = TESIUtil.remove_honor_words(term2)
					sum_sim += TESIUtil.string_similarity(str1, str2)
					qty += 1
				avg = sum_sim/qty
				if(avg > best_avg):
					best_avg = avg
					best = item2
			
			if(best_avg > 0.75):
				best.add_name(term1)
				final_dict[item1.id()] = best
			else:
				final_dict[item1.id()] = item1

		return final_dict

	def _add_in_entities_dictionary(self, dic, string):
		if(string in dic):
			e = dic[string]
			e.add_name(string)
		else:
			e = NamedEntity(string)
			dic[string] = e
		return e

	def _analyze_sentence_with_chunk(self, sentence):
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
					e = self._add_in_entities_dictionary(dic_entities, string)
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
