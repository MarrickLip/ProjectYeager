path = '/Users/Marrick/airfoil_data'

import requests
import re
import time
import os

index_url = 'http://airfoiltools.com/search/airfoils'
all_foils = str(requests.get(index_url).content, 'utf8')

pattern = r"<a href=\"/airfoil/details\?airfoil=(.*?)\""
foil_ids = re.findall(pattern, all_foils)

start_time = time.time()
for i, foil_id in enumerate(foil_ids):
	start_time = time.time()

	folder_path = os.path.join(path, foil_id)
	if os.path.exists(folder_path):
		continue
	else:
		os.mkdir(folder_path)
	folder_path = os.path.join(folder_path, '')

	url = 'http://airfoiltools.com/airfoil/seligdatfile?airfoil=' + foil_id
	foil_coords = str(requests.get(url).content, 'utf8')
	open(folder_path + foil_id + '_selig.txt', 'w').write(foil_coords)

	url = 'http://airfoiltools.com/airfoil/details?airfoil=' + foil_id
	foil_page = str(requests.get(url).content, 'utf8')

	pattern = r"<a href=\"/polar/details\?polar=(.*?)\""
	details_id = re.findall(pattern, foil_page)
	for detail_id in details_id:
		url = 'http://airfoiltools.com/polar/csv?polar=' + detail_id
		polar_csv = str(requests.get(url).content, 'utf8')
		open(folder_path + foil_id + '_polar_' + detail_id + '.csv', 'w').write(polar_csv)

	duration = time.time() - start_time
	print(
		'({} / {}) Downloaded "{}" in {:.2f} seconds.'.format(i + 1, len(foil_ids), foil_id, time.time() - start_time))
