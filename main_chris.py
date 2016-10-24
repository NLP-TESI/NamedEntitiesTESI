#!/usr/bin/python3
#from GOTTESI import *
from Util import TextProcess
from Util import TESIUtil
from NamedEntities.KnowledgeExtractor import KnowledgeExtractor
from NamedEntities.NamedEntity import NamedEntitiesDict
import sys

def main():
	epi_dir = 'episodes'
	epi_pre_dir = 'episodes_preproc'
	entities_file = 'entities.csv'
	relationships_file = 'relationships.csv'

	if('preprocess' in sys.argv):
		print('pre processing text... ', end='')
		TextProcess.pre_process_got_base(epi_dir, epi_pre_dir)
		print('ok')

	if('find_ne' in sys.argv):
		print('identifying named entities...')
		extractor = KnowledgeExtractor(epi_pre_dir)
		tagged = extractor.find_entities(entities_file)
		extractor.find_relationships(tagged, relationships_file)
		print('ok')

	if('merge_ne' in sys.argv):
		print('loadig named entities from file...')
		dic = NamedEntitiesDict.load_entities_dict_from_file(epi_pre_dir, entities_file)
		lst = TESIUtil.dict_to_list(dic)
		final = 0
		for item1 in lst:
			for item2 in lst:
				if(item1 == item2):
					continue
				summ = 0
				qty = 0
				for str1 in item1.terms():
					str1 = TESIUtil.remove_honor_words(str1)
					for str2 in item2.terms():
						str2 = TESIUtil.remove_honor_words(str2)
						summ += TESIUtil.string_similarity(str1, str2)
						qty += 1
				avg = summ/qty
				if(avg > 0.7):
					print(str(avg) + " => " + str(item1.terms()) + " & " + str(item2.terms()))
					final += 1
		print(final)


main()
