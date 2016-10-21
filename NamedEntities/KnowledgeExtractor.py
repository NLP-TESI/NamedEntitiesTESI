from NamedEntities.EpisodeFile import *
from Util import TESIUtil

class KnowledgeExtractor:
	def __init__(self, path):
		self._path = path

	def find_entities(self, file_to_save):
		files = FileSet(self._path)

		entities = {}
		current_index = 0
		for f in files:
			percent = current_index/len(files)*100
			print(str(round(percent, 1)) + "% ("+ str(current_index+1) +" de " + str(len(files)) + ")")
			tagged, entities = f.markup_entities(entities)
			self._save_tagged_text(f.path(), tagged)
			current_index += 1

		self._save_found_entities(self._path, file_to_save, entities)
		distinct_size = len(TESIUtil.dict_to_list(entities))

		print('\n\n' + str(len(entities)) + ' entities found')
		print(str(distinct_size) + ' distinct entities')

		return tagged

	def find_relationships(self, tagged, file_to_save):
		last_entity = None
		last_entity_index = 0
		last_relation = None
		relationships = []

		for sentence in tagged:
			for index, item in enumerate(sentence):
				if('VB' in item[1]):
					last_relation = item[0]
				elif(item[1] in ['HSE', 'NE']):
					if(last_entity is not None):
						if(index-last_entity_index == 2):
							relation = (sentence[index-1][0], last_entity[2], last_entity[0], item[2], item[0])
							relationships.append(relation)
							print(relation)
						elif(last_relation is not None):
							relation = (last_relation, last_entity[2], last_entity[0], item[2], item[0])
							relationships.append(relation)
							print(relation)
					last_entity = item
					last_entity_index = index
					last_relation = None
			

		return 'Hue'

	def _save_tagged_text(self, path, tagged):
		string = ''

		print("Saving tagged text in " + path)

		for sentence in tagged:
			for item in sentence:
				if(item[1] in ['NE', 'HSE']):
					string += ' <entity class="'+item[1]+'" id='+ str(item[2]) +'>' + item[0] + '</entity>' 
				else:
					string += ' ' + item[0]

		string = string.strip()
		TESIUtil.save_file(path, 'tagged_text.txt', string)
	
	def _save_found_entities(self, path, file_to_save, entities):
		lines = []

		print("Saving entities dict in " + path)

		for key in entities:
			item = entities[key]
			tpl = []
			tpl.append(str(key))
			tpl.append(str(item.id()))
			tpl.append(';'.join(item.terms()))
			lines.append( ';'.join(tpl) )
		string = '\n'.join(lines)
		TESIUtil.save_file(path, file_to_save, string)

