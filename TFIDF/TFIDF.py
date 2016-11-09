from NamedEntities.EpisodeFile import FileSet
from Util import TESIUtil
from NamedEntities.NamedEntity import NamedEntitiesDict
import nltk
import re
import math
import os
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
import numpy as np
from sklearn.utils.extmath import randomized_svd
import matplotlib.pyplot as plt
from scipy.spatial.distance import cosine
from operator import itemgetter

class TFIDFCalculator:
	def __init__(self, path, entities_file):
		self._files = FileSet(path)
		self._episodes_map = []
		if(os.path.exists(os.path.join(path, entities_file))):
			self._full_entities_dict = NamedEntitiesDict.load_entities_dict_from_file(path, entities_file)
			self._entities = NamedEntitiesDict.get_entities_fathers_dictionary(self._full_entities_dict)
		else:
			print('Error: Missing entities.csv file. Execute find_ne option before tfidf.')
			exit(0)


	def calculateTFIDF(self):
		if(self._files is None or type(self._files) != FileSet or
			len(self._files) == 0 or self._entities is None or len(self._entities) == 0):
			print('Error: Missing episode files')
		else:
			documents = []
			for episode in self._files:
				doc = Document(episode, self._tokenize_tagged_text(episode.tagged_text()))
				documents.append(doc)
			
			result = self._calculate_tfidf(documents) # Save CSV as dictonary. Does not build the entire matrix
			self._tfidf = result
			# Calculate entire matrix and SVD for it
			self._matrix = self._build_entire_matrix(result)
			self._k = 27
			self._K_Terms, self._K_Docs = self._svd(self._matrix, self._k)

	def _build_entire_matrix(self, tfidf):
		final_terms = {}
		for item in tfidf:
			for t in item:
				final_terms[t] = True

		self._final_tokens = list(final_terms.keys())

		#print(str(len(list(final_terms.keys()))) + " distinct tokens")

		matrix = []
		for i, tfidf_doc in enumerate(tfidf): # for each episode (tfidf)
			vector = []
			for t in final_terms:
				if t in tfidf_doc:
					vector.append(tfidf_doc[t])
				else:
					vector.append(0)
			matrix.append(vector)

		return np.array(matrix).transpose()
		
	def _svd(self, X, k, plot=False):
		U, Sigma, VT = randomized_svd(X, n_components=k, n_iter=7, random_state=42)
		U = np.negative(U)
		VT = np.negative(VT)
		S = [[0 for x in Sigma] for x in Sigma]
		for i in range(len(Sigma)):
			S[i][i] = Sigma[i]

		if(plot):
			print(Sigma)
			index = []
			for i in range(len(Sigma)):
				index.append(i+1)
			plt.scatter(index,Sigma)
			plt.show()

		K_Terms = np.dot(U, S)
		K_Docs = np.dot(S, VT)

		return (K_Terms, K_Docs)

	def _calculate_tfidf(self, documents):
		tf = []
		idf = []

		for d in documents:
			tf.append(self._get_tf_from_doc(d))

		for d in documents:
			idf.append(self._get_idf_from_doc(d, documents))

		tfidf = []
		for i, d in enumerate(documents):
			tfidf_episode = {}

			for t in tf[i]:
				tfidf_episode[t] = tf[i][t] * idf[i][t]
			tfidf.append(tfidf_episode)

			d.episode().save_tfidf(tfidf_episode)
			self._episodes_map.append("SE" + str(d.episode().season()) + " EP" + str(d.episode().number()))

		return tfidf

	def _get_tf_from_doc(self, doc):
		tf = {}

		for t in doc.word_count():
			tf[t] = doc.word_count()[t] / doc.total_words()

		return tf

	def _get_idf_from_doc(self, doc, all_docs):
		idf = {}

		for t in doc.word_count():
			freq = 0
			for d in all_docs:
				if(t in d.word_count()):
					freq += 1
			idf[t] = 1.0 + math.log(len(all_docs)/freq)

		return idf

	def _tokenize_tagged_text(self, tagged_text):
		tokens = []
		while True:
			index_start = TESIUtil.index_of(tagged_text, "<entity")
			index_end = TESIUtil.index_of(tagged_text, "</entity>")

			if(index_start >= 0):
				first_part = tagged_text[:index_start]
				tokens.extend(nltk.word_tokenize(first_part))

				mid_part = tagged_text[index_start:index_end].strip()
				id_entity = mid_part[mid_part.index("id=")+3:mid_part.index(">")]
				tokens.append('__id__' + str(self._full_entities_dict[int(id_entity)].id()))
				tagged_text = tagged_text[index_end+9:].strip()
			else:
				tokens.extend(nltk.word_tokenize(tagged_text))
				break

		# removing punctuation things
		tokens = [x for x in tokens if x not in ['.', ',', "'s"]]
		# just digits and letters
		tokens = [self._normalize_token(x) for x in tokens]
		# removing stop words
		tokens = [x for x in tokens if x not in TESIUtil.ENGLISH_STOP_WORDS]
		# stemming
		#st = LancasterStemmer()
		st = PorterStemmer()
		tokens = [st.stem(x) for x in tokens]
		
		return tokens

	def _normalize_token(self, token):
		if("__id__" in token):
			return token
		else:
			return re.sub('\W', '', token.lower())

	def query(self, svd=False):
		while(True):
			print("Type your query: ")
			query = input()
			query = self._normalize_query(query)
			print("Normalized query: " + query)

			entities_in_query, non_entities_tokens = self._find_entities_in_query(query)
			# stemming
			#st = LancasterStemmer()
			st = PorterStemmer()
			non_entities_tokens = [st.stem(x) for x in non_entities_tokens]

			final_query = []
			for item in entities_in_query:
				tk = '__id__' + str(item)
				final_query.append(tk)

			for item in non_entities_tokens:
				final_query.append(item)

			print("Entities in query: ")
			for item in entities_in_query:
				print(str(item) + ": " + str(self._entities[item]))
			print("Final query: " + str(final_query))

			if(svd):
				sim = self._similarity_svd(final_query)
			else:
				sim = self._similarity_tfidf_vectors(final_query)

			temp_eps = self._episodes_map
			sort = [list(x) for x in (zip(*sorted(zip(sim, temp_eps), key=itemgetter(0))))]
			result_score = sort[0]
			result_ep = sort[1]
			
			for i in range(55):
				print(result_ep[i] + ": " + str(result_score[i]))

			print("Query again? (y/n): ")
			opt = input()
			if(opt != 'y'):
				break

	def _similarity_svd(self, final_query):
		Q = []
		for i in range(self._k):
			Q.append(0)

		for item in final_query:
			index = TESIUtil.index_of(self._final_tokens, item)
			
			if(index != -1):
				for p in range(self._k):
					Q[p] += (self._K_Terms[index][p])/self._k

		temp_docs = self._K_Docs.transpose()
		sim = []
		for ep in range(len(temp_docs)):
			sim.append(cosine(Q, temp_docs[ep]))

		return sim

	def _similarity_tfidf_vectors(self, final_query):
		sim = []

		for i in range(len(self._tfidf)):
			Q = []
			V = []

			for term in self._final_tokens:
				if(term in final_query):
					Q.append(1)
				else:
					Q.append(0)
				if(term in self._tfidf[i]):
					V.append(self._tfidf[i][term])
				else:
					V.append(0)

			sim.append(cosine(Q, V))

		return sim

	def _normalize_query(self, query):
		query_tokens = nltk.word_tokenize(query)
		# removing punctuation things
		query_tokens = [x for x in query_tokens if x not in ['.', ',', "'s"]]
		# just digits and letters
		query_tokens = [self._normalize_token(x) for x in query_tokens]
		# removing stop words
		query_tokens = [x for x in query_tokens if x not in TESIUtil.ENGLISH_STOP_WORDS]
		query = ' '.join(query_tokens).strip()
		return query

	def _find_entities_in_query(self, query):
		entities = {}
		found_entities = {}
		query_without_entities = query

		tokenized_query = nltk.word_tokenize(query)
		i = len(tokenized_query)
		while(i > 0):
			start_index = 0
			end_index = i
			temp_query_without_entities = query_without_entities

			while(end_index <= len(tokenized_query)):
				actual_str = ' '.join(tokenized_query[start_index:end_index])

				for key in self._entities:
					for t in self._entities[key]:
						normalized_t = self._normalize_query(t)
				
						if(normalized_t is None or len(normalized_t) == 0):
							continue

						if(normalized_t == actual_str and normalized_t in query_without_entities):
							entities[key] = True
							temp_query_without_entities = re.sub(normalized_t, ' ', temp_query_without_entities)

				start_index += 1
				end_index += 1

			query_without_entities = temp_query_without_entities
			i -= 1

		'''
		# Find in query based on entities
		for key in self._entities:
			for t in self._entities[key]:
				normalized_t = self._normalize_query(t)
				
				if(normalized_t is None or len(normalized_t) == 0):
					continue

				if(normalized_t in query):
					entities[key] = True
					found_entities[normalized_t]
					# query_without_entities = re.sub(normalized_t, ' ', query_without_entities)
		'''
		# Find in entities based on remaining query
		'''others_tokenized = nltk.word_tokenize(query_without_entities)
		for rt in others_tokenized:
			for key in self._entities:
				for t in self._entities[key]:
					t_list = self._normalize_query(t).split()
					if('' in t_list):
						t_list.remove('')

					if(normalized_t is None or len(normalized_t) == 0):
						continue

					if(rt in t_list):
						entities[key] = True
						query_without_entities = re.sub(rt, ' ', query_without_entities)
		'''
		return (list(entities.keys()), nltk.word_tokenize(query_without_entities))


class Document:
	def __init__(self, episode, tokens):
		self._episode = episode
		self._tokens = tokens
		self._word_count = {}

		for t in tokens:
			if(t in self._word_count):
				self._word_count[t] += 1
			else:
				self._word_count[t] = 1

		self._total_words = len(list(self._word_count.keys()))

	def word_count(self):
		return self._word_count

	def total_words(self):
		return self._total_words

	def episode(self):
		return self._episode