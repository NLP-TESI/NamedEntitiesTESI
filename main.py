#!/usr/bin/python3

from findNamedEntities import *

episodes = EpisodesFiles("./episodes")

namedEntities = NamedEntities(episodes)

for entity in namedEntities:
	print(entity)
	
print (str(len(namedEntities)) + " entidades")
