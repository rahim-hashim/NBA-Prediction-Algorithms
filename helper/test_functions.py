import re
import os
import sys
import numpy as np
import pandas as pd
from string import ascii_lowercase
from collections import defaultdict

# Custom Functions
from player_scraper import scrape_all_players

ROOT = os.getcwd()
df_players_meta, df_players_data, df_players_gamelogs  = scrape_all_players(ROOT, THREAD_FLAG=True)