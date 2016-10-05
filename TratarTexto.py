import re
from TESIUtil import *

def pre_processar_base_got(origem_path, destino_path):
	criar_recriar_diretorio(destino_path)

	for season in os.listdir(origem_path):
		path_season_destino = montar_caminho_diretorios(destino_path, season)
		path_season_origem = montar_caminho_diretorios(origem_path, season)
		
		criar_recriar_diretorio( path_season_destino )

		for filename in os.listdir( path_season_origem ):
			ep = open( montar_caminho_diretorios(origem_path, season, filename) )
			text = ep.read()
			_pre_processar_episodio(path_season_destino, filename, text)

def _pre_processar_episodio(path_destino, filename, texto):
	lines_text = texto.split("\n")
	lines_text = [x.strip() for x in lines_text]

	nome_episodio = _recuperar_nome_episodio(filename)
	numero_episodio = _recuperar_num_episodio(texto)

	ep_dir = montar_caminho_diretorios(path_destino, numero_episodio)
	criar_recriar_diretorio(ep_dir)

	mortes_epi = _encontrar_mortes_no_episodio(lines_text, filename)
	texto_preprocessado = _pre_processar_texto(lines_text)

	salvar_arquivo(ep_dir, 'ep_name.txt', nome_episodio)
	salvar_arquivo(ep_dir, 'original.txt', texto)
	salvar_arquivo(ep_dir, 'deaths.txt', mortes_epi)
	salvar_arquivo(ep_dir, 'clean_text.txt', texto_preprocessado)

def _encontrar_mortes_no_episodio(lines_text, filename):
	termos_secao_mortes = ['Deaths', 'DeathsEdit', 'Deaths Edit']
	n = -1

	for t in termos_secao_mortes:
		n = index_of(lines_text, t)
		if(n != -1):
			break
	
	mortes_list = []
	if(n != -1):
		n = n + 1
		mortes_list = lines_text[n:]
		n = index_of(mortes_list, "")
		mortes_list = mortes_list[:n]

	return "\n".join(mortes_list)

def _pre_processar_texto(lines_text):
	lines_text = _cortar_inicio_texto(lines_text)
	lines_text = _remover_linhas_inuteis(lines_text)
	lines_text = _cortar_final_texto(lines_text)

	return "\n".join(lines_text).replace('Edit', '').replace('\n', '. ').replace('  ', ' ').replace('..', '.')

def _cortar_inicio_texto(lines_text):
	n = lines_text.index('Contents[show]') + 1
	lines_text = lines_text[n:]
	return lines_text

def _remover_linhas_inuteis(lines_text):
	stop_lines_list = ['Contents[show]', 'Plot', 'PlotEdit', 'Plot Edit', 'Synopsis', 'SynopsisEdit', 'Summary', 'SummaryEdit']
	lines_text = [x for x in lines_text if x not in stop_lines_list]
	return lines_text

def _cortar_final_texto(lines_text):
	termos_finais = ['Recap', 'RecapEdit', 'Appearances', 'AppearancesEdit', 'Appearances Edit']
	n = -1

	for t in termos_finais:
		n = index_of(lines_text, t)
		if(n != -1):
			lines_text = lines_text[:n]
			break

	return lines_text

def _recuperar_nome_episodio(filename):
	return filename.replace('_', ' ').replace('.txt', '').replace('(episode)', '').strip().title()

def _recuperar_num_episodio(texto):
	return re.findall(r'\b[Ee]pisode [0-9][0-9]?', texto)[0].replace('Episode ', '')