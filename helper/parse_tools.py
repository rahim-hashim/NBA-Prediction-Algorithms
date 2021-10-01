import re

def data_type_parse(tag_soup):
  '''Searches for tag id'''
  id_pattern = 'id="([A-Za-z0-9_/\\-]*)'
  reg_result = re.search(id_pattern, str(tag_soup))
  reg_result = reg_result.group(1)
  data_type = reg_result.replace('_sh','').replace('div_','')
  return data_type

def num_convert(value):
  '''Converts str data value to int, float, or stays as str'''
  # int
  if value.isdigit() or (value[1:] == '-' and value[1:].isdigit()):
    return int(value)
  # float
  try:
    float(value)
    return float(value)
  # str
  except:
    return value