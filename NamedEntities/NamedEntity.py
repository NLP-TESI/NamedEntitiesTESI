import os

class NamedEntity:
	ID = 0

	def __init__(self, last=0, name=None):
		self._global_freq = 0
		self._last_index = last
		self._terms = {}
		if(name is not None):
			self.inc_frequency()
			self._terms[name] = True
			self._id = NamedEntity.ID
			NamedEntity.ID += 1

	def terms(self):
		return self._terms

	def add_name(self, name, index):
		self._terms[name] = True
		self.inc_frequency()
		if(int(index) > int(self._last_index)):
			self._last_index = index

	def inc_frequency(self):
		self._global_freq += 1

	def id(self):
		return self._id

	def set_id(self, i):
		self._id = i
		if(i > NamedEntity.ID):
			NamedEntity.ID = i+1

	def change_id(self, i):
		self._id = i

	def set_terms(self, lst):
		self._terms = lst

	def last_index(self):
		return self._last_index

	def frequency(self):
		return self._global_freq

	def add_entity(self, item):
		for term in item.terms():
			self._terms[term] = True
		self._global_freq += item.frequency()
		if(self._last_index < item.last_index()):
			self._last_index = item.last_index()

	def __str__(self):
		return str(self._terms) + "\n" + str(self._global_freq)


class NamedEntitiesDict:
	@staticmethod
	def load_entities_dict_from_file(path, filename):
		f = open(os.path.join(path, filename), 'r')
		lines = f.read().split('\n')

		entities_dict = {}

		for line in lines:
			values = line.split(';')
			idt = int(values[0])
			ftr = int(values[1])
			terms = values[2:]

			entity = NamedEntity()
			entity.set_id(idt)
			entity.set_terms(terms)
			
			if(ftr not in entities_dict):
				entities_dict[ftr] = entity
				entities_dict[idt] = entity
			else:
				entities_dict[idt] = entities_dict[ftr]

		return entities_dict
