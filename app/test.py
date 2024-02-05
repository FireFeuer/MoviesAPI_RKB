import pandas as pd
import os

import sys
import os
import re

def similar_movies_regex(movie_list, regex_pattern):
    regex_pattern = re.compile(regex_pattern, re.IGNORECASE)
    for movie in movie_list:
        match = regex_pattern.search(movie)
        if match:
            return True
    return False



current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

csv_path = current_dir + '\movies.csv'
df = pd.read_csv(csv_path)
column = df['title']
list_column = list(column)




if similar_movies_regex(list_column, 'These Amazing '):
    print('Фильм найден!')
else:
    print('Фильм не найден.')
