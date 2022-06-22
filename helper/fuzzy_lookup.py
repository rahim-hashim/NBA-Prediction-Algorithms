# Author: adapted from Francisco Javier Carrera
# Source: https://www.datacamp.com/community/tutorials/fuzzy-string-python
import re
import numpy as np
from collections import defaultdict, Counter

WEBSITE_URL = 'https://www.basketball-reference.com'

def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
  """ levenshtein_ratio_and_distance:
      Calculates levenshtein distance between two strings.
      If ratio_calc = True, the function computes the
      levenshtein distance ratio of similarity between two strings
      For all i and j, distance[i,j] will contain the Levenshtein
      distance between the first i characters of s and the
      first j characters of t
  """
  # Initialize matrix of zeros
  rows = len(s)+1
  cols = len(t)+1
  distance = np.zeros((rows,cols),dtype = int)

  # Populate matrix of zeros with the indeces of each character of both strings
  for i in range(1, rows):
    for k in range(1,cols):
      distance[i][0] = i
      distance[0][k] = k

  # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
  for col in range(1, cols):
    for row in range(1, rows):
      if s[row-1] == t[col-1]:
        cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
      else:
        # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
        # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
        if ratio_calc == True:
          cost = 2
        else:
          cost = 1
      distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                            distance[row][col-1] + 1,          # Cost of insertions
                            distance[row-1][col-1] + cost)     # Cost of substitutions
  if ratio_calc == True:
    # Computation of the Levenshtein Distance Ratio
    Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
    return Ratio
  else:
    # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
    # insertions and/or substitutions
    # This is the minimum number of edits needed to convert string a to string b
    return "The strings are {} edits away".format(distance[row][col])

def fuzzy_matching(player_name, playerTable):
  FUZZY_THRESHOLD = 0.7
  fuzzy_matches = defaultdict(lambda: defaultdict(list))
  max_fuzzy = [0, None]  # [score, name]
  for index, row in enumerate(playerTable):
    row_player_name = re.findall('.html">(.*?)</a>', str(row))[0]
    fuzzy_ratio = levenshtein_ratio_and_distance(player_name.lower(), row_player_name.lower(), ratio_calc=True)
    if fuzzy_ratio > max_fuzzy[0]:
      max_fuzzy = [fuzzy_ratio, row_player_name]
    if fuzzy_ratio > FUZZY_THRESHOLD:
      playerURL = re.findall('a href="(.*?)">', str(row))
      playerURL = WEBSITE_URL + playerURL[0]
      fuzzy_matches[row_player_name]['fuzzy_score'].append(fuzzy_ratio)
      fuzzy_matches[row_player_name]['url'].append(playerURL)
    else:
      continue
  if len(list(fuzzy_matches.keys())) > 0:
    for key in list(fuzzy_matches.keys()):
      fuzzy_score = round(fuzzy_matches[key]['fuzzy_score'][0], 3)
      print('  {} (match score={})'.format(key, str(fuzzy_score)))
    playerName = max_fuzzy[1]
    playerURL = fuzzy_matches[playerName]['url'][0]
    print('Best match: {}'.format(max_fuzzy[1]))
    return playerName, playerURL
  else:
    return '', ''
