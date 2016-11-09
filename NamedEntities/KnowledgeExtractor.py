from NamedEntities.EpisodeFile import *
from Util import TESIUtil
import re
from collections import OrderedDict

class KnowledgeExtractor:
	def __init__(self, path):
		self._path = path

	def find_entities(self, file_to_save):
		files = FileSet(self._path)

		entities = {}
		all_tagged = []
		for current_index, f in enumerate(files):
			percent = (current_index+1)/len(files)*100
			print("\r"+str(round(percent, 1)) + "% ("+ str(current_index+1) +" de " + str(len(files)) + ")", end="")
			tagged, entities = f.markup_entities(entities)
			self._save_tagged_text(f.path(), tagged)
			all_tagged += tagged

		self._save_found_entities(self._path, file_to_save, entities)
		distinct_size = len(TESIUtil.dict_to_list(entities))

		print('\n\n' + str(len(entities)) + ' entities found')
		print(str(distinct_size) + ' distinct entities\n')

		return all_tagged

	def _get_composed_verbs(self, sentence, start, end):
		composed_verb = sentence[start][0]
		aux = ""
		if('VB' in sentence[start][1]):
			for index in range(start-1,end-1,-1):
				if(index < 0 or start-index > 4):
					break
				item = sentence[index]
				aux = item[0] + " " + aux
				if("VB" in item[1]):
					composed_verb = aux + composed_verb
					break
		return composed_verb

	def find_relationships(self, tagged, file_to_save):
		relationships = []
		relationships_keys = {}
		stop_words = ["''", "King"]

		print("identifying relationships...")

		for index_sentence, sentence in enumerate(tagged):
			last_entity = None
			last_entity_index = 0
			last_relation = None

			percent = (index_sentence+1)/len(tagged)*100
			print("\r"+str(round(percent, 1)) + "% ("+ str(index_sentence+1) +" de " + str(len(tagged)) + ")", end="")

			for index, item in enumerate(sentence):
				if( len(item[0]) == 1 ):
					continue
				if('VB' in item[1]):
					last_relation = self._get_composed_verbs(sentence, index, last_entity_index)
				elif( index < len(sentence)-1 and 'IN' == item[1] and 'DT' == sentence[index+1][1]):
					last_relation = item[0] + " " + sentence[index+1][0]
				elif(item[1] in ['HSE', 'NE']):
					if(last_entity is not None):
						if(index-last_entity_index == 2 and len(sentence[index-1][0])>1 and sentence[index-1][0] not in stop_words ):
							relation_key = sentence[index-1][0]
							relation = (relation_key, last_entity[2], last_entity[0], item[2], item[0])
							relationships.append(relation)
							if relation_key not in relationships_keys:
								relationships_keys[relation_key] = 0
							relationships_keys[relation_key] += 1
							#print(relation)
						elif(last_relation is not None and len(re.findall(r"[^\w\s']", last_relation)) == 0 and last_relation not in stop_words):
							relation = (last_relation, last_entity[2], last_entity[0], item[2], item[0])
							relationships.append(relation)
							relation_key = last_relation
							if relation_key not in relationships_keys:
								relationships_keys[relation_key] = 0
							relationships_keys[relation_key] += 1
							#print(relation)
					last_entity = item
					last_entity_index = index
					last_relation = None

		relationships_keys = OrderedDict(sorted(relationships_keys.items(), key=lambda t: t[0]))
		relationships.sort(key=lambda t: t[0])
		self._save_relationships_csv(relationships, file_to_save)
		self._save_relationships_keys_csv(relationships_keys, file_to_save)

		print('\n\n' + str(len(relationships)) + ' relationships found\n')

		return relationships

	def _save_relationships_keys_csv(self, relationships_keys, file_to_save):
		outfile = open("keys_"+file_to_save, 'w+')
		outfile.write("relationship,frequency\n")
		for relationship in relationships_keys:
			outfile.write(relationship+","+str(relationships_keys[relationship])+"\n")
		outfile.close()

	def _save_relationships_csv(self, relationships, file_to_save):
		outfile = open(file_to_save, 'w+')
		outfile.write("entity1,relationship,entity2\n")
		for relationship in relationships:
			outfile.write(relationship[2]+","+relationship[0]+","+relationship[4]+"\n")
		outfile.close()

	def _save_tagged_text(self, path, tagged):
		string = ''

		#print("Saving tagged text in " + path)

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

		#print("Saving entities dict in " + path)

		for key in entities:
			item = entities[key]
			tpl = []
			tpl.append(str(key))
			tpl.append(str(item.id()))
			tpl.append(';'.join(item.terms()))
			lines.append( ';'.join(tpl) )
		string = '\n'.join(lines)
		TESIUtil.save_file(path, file_to_save, string)
