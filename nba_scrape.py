import os
import sys
import numpy as np
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
from collections import Counter, OrderedDict, defaultdict
pd.options.mode.chained_assignment = None  # default='warn'

from helper import TeamNames
from helper.bettingLinesScraper import scrape

def scrape_lines():
  start_year = 2020 #@param {type:"integer"}
  end_year = 2021 #@param {type:"integer"}

  betting_lines_dict = scrape(start_year, end_year)
  return betting_lines_dict

betting_line_dict = scrape_lines()
print(betting_line_dict)