import distance
import jellyfish

names = [
			['Jon Snow', 'Jon', 'Snow', 'Lord Snow', 'Jon Paul', 'Lord Joseph'],
			['Ned Stark', 'Ned', 'Stark', 'Lord Stark', 'Lord Eddard', 'Eddard Stark'],
			['Theon Greyjoy', 'Theon', 'Greyjoy', 'Lord Greyjoy', 'Yara Greyjoy']
		]

def comparar():
	result = ""
	for cjt in names:
		for name in cjt[1:]:
			jaro = jellyfish.jaro_distance(cjt[0], name)
			jaro_winkler = jellyfish.jaro_winkler(cjt[0], name)
			jaccard = distance.jaccard(cjt[0], name)
			leven = distance.nlevenshtein(cjt[0], name)

			result += cjt[0] + "," + name + "," + "jaro" + "," + str(jaro) + "\n"
			result += cjt[0] + "," + name + "," + "jaro winkler" + "," + str(jaro_winkler) + "\n"
			result += cjt[0] + "," + name + "," + "jaccard" + "," + str(jaccard) + "\n"
			result += cjt[0] + "," + name + "," + "levenshtein" + "," + str(leven) + "\n"

	return result

string = "nome 1, nome 2, metrica, resultado\n"
string += comparar()
f = open('resultado_metricas.csv', 'w')
f.write(string)
f.close()