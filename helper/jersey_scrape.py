import os
import sys
import time
import requests
import pandas as pd
from tqdm import tqdm
import pickle as pickle
from bs4 import BeautifulSoup
from collections import defaultdict

def scrape_jersey(jersey_df, jersey_num):
	url = "https://www.basketball-reference.com/friv/numbers.fcgi?number={}".format(jersey_num)
	r = requests.get(url)
	if r.status_code != 200:
		if r.status_code == 429:
			print('Too many requests, blocked by Basketball Reference. Wait before retrying...')
			sys.exit()
		else:
			sys.exit('Error, status code: {}'.format(r.status_code))
	soup = BeautifulSoup(r.content, 'html.parser')
	table = soup.find('table', {'id': 'numbers'})
	# No players with this jersey number
	if not table:
		print('Jersey Number {}: 0 players'.format(jersey_num))
		return jersey_df
	table_rows = table.find_all('tr')
	print('Jersey Number {}: {} players'.format(jersey_num, len(table_rows)))
	for row in table_rows:
		player = row.find('th', {'data-stat': 'player'}).text.strip('*').strip()
		cols = row.find('td')
		if player and cols:
			team_years = cols.text.strip()
			for team_string in team_years.split(')')[:-1]:
				team, years = team_string.split(' (')
				years_int = [int(year) for year in years.split(', ')]
				# one less to make 2020 -> 2019-2020
				years_updated = [1999+year if year <= 23 else 1899 + year for year in years_int]
				years = [str(year)+'-'+str(year+1)[2:] for year in years_updated]
				for year in years:
					jersey_df = jersey_df.append({'player': player, 'team': team, 'year': year, 'jersey_number': jersey_num}, ignore_index=True)
	return jersey_df

if __name__ == '__main__':
	print('Scraping Basketball Reference for jersey numbers...')
	jersey_df = pd.DataFrame(columns=['player', 'team', 'year', 'jersey_number'])
	# jersey numbers can range from 00 to 99
	jersey_numbers_str = [str(num).zfill(1) for num in range(10)] + [str(num).zfill(2) for num in range(100)]
	for jersey_number in tqdm(jersey_numbers_str):
		jersey_df = scrape_jersey(jersey_df, jersey_number)
		data_path = os.path.join(os.getcwd(), 'data', 'jersey_df.pkl')
		with open(data_path, 'wb') as f:
			pickle.dump(jersey_df, f)
		# wait 15 second to avoid getting blocked
		time.sleep(15)
	print('Scrape complete. Pickle file saved to jersey_df.pkl')
	print(' Number of players: {}'.format(len(jersey_df)))