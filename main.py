#!/usr/bin/python3
from GOTTESI import *
import TratarTexto
from NamedEntities import *
from findRelationship import *

def main():
    epi_dir = 'episodes'
    epi_pre_dir = 'episodes_preproc'

    TratarTexto.pre_processar_base_got(epi_dir, epi_pre_dir)
    files = GOTFiles(epi_pre_dir)
    bag = BagOfEntities(files, 'lists_of_entities.txt')
    bag.save_in_file()

    #number of entities
    print(str(len(bag)) + " entidades")

    #getting all the sentences to use in relationships preprocessing
    episodes = EpisodesFiles("./"+epi_dir)
    episodes_sentences = EpisodesSentences("./"+epi_dir)

    #getting all the relationships
    relationships = Relationships(bag, episodes_sentences)
    print(str(len(relationships)) + " relationships")

main()
