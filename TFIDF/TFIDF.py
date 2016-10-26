from NamedEntities.EpisodeFile import FileSet
from Util import TESIUtil
import nltk
import re
import math

class TFIDFCalculator:
	def __init__(self, path):
		self._files = FileSet(path)

	def calculateTFIDF(self):
		if(self._files is None or type(self._files) != FileSet or
			len(self._files) == 0):
			print('Error: Missing episode files')
		else:
			documents = []
			for episode in self._files:
				doc = Document(episode, self._tokenize_tagged_text(episode.tagged_text()))
				documents.append(doc)
			
			self._calculate_tfidf(documents)

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
				tokens.append('__id__' + id_entity)
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
		
		return tokens

	def _normalize_token(self, token):
		if("__id__" in token):
			return token
		else:
			return re.sub('\W', '', token.lower())

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