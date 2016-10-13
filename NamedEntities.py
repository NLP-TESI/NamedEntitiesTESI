import os
import TESIUtil

class NamedEntity:
	def __init__(self, init_name=None):
		if(init_name != None):
			self.names = [init_name]
		else:
			self.names = []

	def contains(self, name):
		return TESIUtil.index_of(self.names, name) != -1

	def add(self, name):
		if(not self.contains(name)):
			self.names.append(name)

	def __len__(self):
		return len(self.names)

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i >= len(self.names):
			raise StopIteration
		else:
			self.i += 1
			return self.names[self.i-1]

	def __str__(self):
		return str(self.names)

class BagOfEntities:
	def __init__(self, got_files, lists_path):
		self._dic = {} # key: name ; value: NamedEntity
		self._entities_list = []
		self._buffer_similarity = {}
		self._lists_path = lists_path

		if(os.path.exists(lists_path)):
			self._init_by_files()
		else:
			self._init_by_got_files(got_files)

	def __iter__(self):
		self.iterator = 0
		self._keys = [ ent for ent in self._dic ]
		return self

	def __next__(self):
		if self.iterator >= len(self._keys):
			raise StopIteration
		else:
			self.iterator += 1
			return self._keys[self.iterator-1]

	def _init_by_files(self):
		lists_file = open(self._lists_path)

		for line in lists_file.read().split('\n'):
			entity = NamedEntity()
			for name in line.split(','):
				if(name == ''):
					continue
				entity.add(name)
				self._dic[name] = entity
			self._entities_list.append(entity)

		lists_file.close()

	def _init_by_got_files(self, got_files):
		i = 1
		for ep in got_files:
			print(i)
			for entity in ep.get_named_entities():
				self.add_name(entity)
			i = i + 1

	def __len__(self):
		return len(self._dic)

	def add_name(self, name):
		if(name not in self._dic):
			entity = self._find_nearst_entity(name)
			if(entity == None):
				new_entity = NamedEntity(name)
				self._dic[name] = new_entity
				self._entities_list.append(new_entity)
			else:
				entity.add(name)
				self._dic[name] = entity

	def keys(self):
		return self._dic.keys()

	def get(self, name):
		return self._dic[name]

	def get_entities_lists(self):
		return self._entities_list

	def save_in_file(self):
		file_lists = open(self._lists_path, 'w')
		out = ""
		for lst in self._entities_list:
			out += ",".join(lst) + '\n'

		file_lists.write(out)


	def _find_nearst_entity(self, name):
		best = 0
		choice = None

		for key in self._dic:
			entity = self._dic[key]
			total = 0
			n = 0

			for term1 in [name]+entity.names:
				for term2 in [name]+entity.names:
					if(term1 != term2):
						if( (term1+"#"+term2) in self._buffer_similarity):
							total += self._buffer_similarity[(term1+"#"+term2)]
						else:
							val = TESIUtil.string_similarity(term1, term2)
							self._buffer_similarity[(term1+"#"+term2)] = val
							total += val
						n = n + 1

			avg = total/n
			if(avg > best and avg > 0.79):
				best = avg
				choice = entity

		return choice

	def __str__(self):
		return str(self._dic)
