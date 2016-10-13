import os
import shutil
import jellyfish
import distance
import SmithWaterman

def criar_recriar_diretorio(dir_path):
	if (os.path.isdir(dir_path)):
		shutil.rmtree(dir_path)
	os.makedirs(dir_path)

def salvar_arquivo(path, filename, texto):
	text_file = open(montar_caminho_diretorios(path, filename), 'w')
	text_file.write(texto)
	text_file.close()

def montar_caminho_diretorios(*paths):
	path = "."
	for p in paths:
		path += "/" + p
	return path

def index_of(lista, value):
	try:
		n = lista.index(value)
		return n
	except ValueError:
		return -1

def string_similarity(str1, str2):
	return jellyfish.jaro_winkler(str1, str2)*0.8 + SmithWaterman.distance(str1, str2)*0.1 + distance.nlevenshtein(str1, str2)*0.1
