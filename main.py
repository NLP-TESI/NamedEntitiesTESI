#!/usr/bin/python3

from findNamedEntities import *
from findRelationship import *

episodes = EpisodesFiles("./episodes")

namedEntities = NamedEntities(episodes)

#for entity in namedEntities:
#	print(entity)

print (str(len(namedEntities)) + " entidades")

episodes_sentences = EpisodesSentences("./episodes")

relationships = Relationships(namedEntities, episodes_sentences)

print (str(len(relationships)) + " relationships")
