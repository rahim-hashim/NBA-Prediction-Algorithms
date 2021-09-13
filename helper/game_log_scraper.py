import re
import os
import sys
import time
import requests
import datetime
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle as pickle
from timeit import timeit
from bs4 import BeautifulSoup
from collections import defaultdict

def game_log_scraper(gamelog):
  print(gamelog)
