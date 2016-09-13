# this files isn't used anymore
import nltk
import os

named_entities = {}

def analizeTree(parent):
	for node in parent:
		if type(node) is nltk.Tree:
			analizeTree(node)

	label = parent.pos()[0][1]
	if(label == 'GPE' or label == 'PERSON' or label == 'ORGANIZATION'):
		named_entities[parent.pos()[0][0][0]] = label

for seasons in os.listdir('episodes'):
	for filename in os.listdir('episodes/' + seasons):
		ep = open('episodes/' + seasons + '/' + filename, 'r')
		text = ep.read()
		tokenized = nltk.word_tokenize(text)
		tagging = nltk.pos_tag(tokenized)
		result = nltk.ne_chunk(tagging)
		break
	break

#print(tokenized)
#print(tagging)
print(result)

#analizeTree(result)

#for values in named_entities:
#	print values + "(" + named_entities[values] + ")"

#print(str(len(named_entities)) + " tokens")
