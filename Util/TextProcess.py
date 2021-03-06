import re
from Util.TESIUtil import *

def pre_process_got_base(origem_path, destino_path):
	create_or_replace_dir(destino_path)

	for season in os.listdir(origem_path):
		path_season_destino = build_dir_path(destino_path, season)
		path_season_origem = build_dir_path(origem_path, season)

		create_or_replace_dir( path_season_destino )

		for filename in os.listdir( path_season_origem ):
			ep = open( build_dir_path(origem_path, season, filename) )
			text = ep.read()
			_pre_process_episode(path_season_destino, filename, text)

def _pre_process_episode(path_destino, filename, texto):
	lines_text = texto.split("\n")
	lines_text = [x.strip() for x in lines_text]

	ep_name = _get_episode_name(filename)
	ep_number = _get_episode_number(texto)

	ep_dir = build_dir_path(path_destino, ep_number)
	create_or_replace_dir(ep_dir)

	mortes_epi = _get_deaths_in_episode(lines_text, filename)
	preprocessed_text = _pre_process_text(lines_text)

	save_file(ep_dir, 'ep_name.txt', ep_name)
	save_file(ep_dir, 'ep_number.txt', ep_number)
	save_file(ep_dir, 'original.txt', texto)
	save_file(ep_dir, 'deaths.txt', mortes_epi)
	save_file(ep_dir, 'clean_text.txt', preprocessed_text)

def _get_deaths_in_episode(lines_text, filename):
	terms_death_section = ['Deaths', 'DeathsEdit', 'Deaths Edit']
	n = -1

	for t in terms_death_section:
		n = index_of(lines_text, t)
		if(n != -1):
			break

	deaths_list = []
	if(n != -1):
		n = n + 1
		deaths_list = lines_text[n:]
		n = index_of(deaths_list, "")
		deaths_list = deaths_list[:n]

	return "\n".join(deaths_list)

def _pre_process_text(lines_text):
	lines_text = _cut_text_start(lines_text)
	lines_text = _remove_useless_lines(lines_text)
	lines_text = _cut_text_end(lines_text)

	result = "\n".join(lines_text).replace('Edit', '').replace('\n', '. ').replace(' .', '.')
	result = re.sub('( )( )+', ' ', result)
	result = re.sub('(\.)(\.)+', '.', result)
	return result

def _cut_text_start(lines_text):
	n = lines_text.index('Contents[show]') + 1
	lines_text = lines_text[n:]
	return lines_text

def _remove_useless_lines(lines_text):
	stop_lines_list = ['Contents[show]', 'Plot', 'PlotEdit', 'Plot Edit', 'Synopsis', 'SynopsisEdit', 'Summary', 'SummaryEdit']
	lines_text = [x for x in lines_text if x not in stop_lines_list]
	return lines_text

def _cut_text_end(lines_text):
	finals_terms = ['Recap', 'RecapEdit', 'Appearances', 'AppearancesEdit', 'Appearances Edit']
	n = -1

	for t in finals_terms:
		n = index_of(lines_text, t)
		if(n != -1):
			lines_text = lines_text[:n]
			break

	return lines_text

def _get_episode_name(filename):
	return filename.replace('_', ' ').replace('.txt', '').replace('(episode)', '').strip().title()

def _get_episode_number(texto):
	return re.findall(r'\b[Ee]pisode [0-9][0-9]?', texto)[0].replace('Episode ', '')
