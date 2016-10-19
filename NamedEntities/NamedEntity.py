import os

class NamedEntity:
	ID = 0

	def __init__(self, name=None):
		self._terms = {}
		if(name is not None):
			self._terms[name] = True
			self._id = NamedEntity.ID
			NamedEntity.ID += 1

	def terms(self):
		return self._terms

	def add_name(self, name):
		self._terms[name] = True

	def id(self):
		return self._id

	def set_id(self, i):
		self._id = i
		if(i > NamedEntity.ID):
			NamedEntity.ID = i+1

	def set_terms(self, lst):
		self._terms = lst

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
