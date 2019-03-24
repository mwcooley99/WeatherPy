#%% [markdown]
# # Introduction
# State notebook purpose here
#%% [markdown]
# ### Imports
# Import libraries and write settings here.

#%%
# Data manipulation
import pandas as pd
import numpy as np

# Options for pandas
pd.options.display.max_columns = 50
pd.options.display.max_rows = 30

# Display all cell outputs
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'

from IPython import get_ipython, display
ipython = get_ipython()

# autoreload extension
if 'autoreload' not in ipython.extension_manager.loaded:
    get_ipython().run_line_magic('load_ext', 'autoreload')

get_ipython().run_line_magic('autoreload', '2')

# Visualizations
import matplotlib.pyplot as plt
import seaborn as sn

# Import APTs
from assets.api_keys import api_key

# Additional modules
from citipy import citipy
import requests
from requests.auth import HTTPBasicAuth
import json

#%% [markdown]
# # Analysis/Modeling
# Do work here
#%% [markdown]
# ### Create a uniformly distributed DataFrame of cities across Latitudes and Longitudes 

#%%
# Create Long and Latitude file if it hasn't already been created
try:
    city_df = pd.read_pickle('assets/city_df')
except IOError:
    # Get a representative sample of longitude and latitudes
    lats = np.random.uniform(-90., 90., 1500)
    longs = np.random.uniform(-180., 180., 1500)
    city_df = pd.DataFrame({'Latitude': lats, 'Longitude': longs })
    pd.to_pickle(city_df, 'assets/city_df')


#%%
city_df.head()


#%%
# Create the base url
base_url = f'http://api.openweathermap.org/data/2.5/find?'


#%%
# Test the API
test_city = "London,uk"
params = {'q': test_city, 'APPID': api_key}
response = requests.get(base_url, params=params)
print(json.dumps(response.json(), indent=4, sort_keys=True))


#%%
# Find cities closest to the urls (assuming they exist, otherwise resturn Nan)
def get_nearest_city(coor):
    city = citipy.nearest_city(coor['Latitude'], coor['Longitude'])
    return city.city_name + ',' + city.country_code
    

city_df.head()

#%%
if not 'city' in city_df.columns:
    print('finding closests cities')
    city_df['city'] = city_df.apply(get_nearest_city, axis=1)
    pd.to_pickle(city_df, 'assets/city_df')
city_df.head()

#%%
# Check for Nan cities
num_of_na = len(city_df[city_df['city'].isna()])
print(f'There were {num_of_na} cities')


#%%


#%% [markdown]
# # Results
# Show graphs and stats here
#%% [markdown]
# # Conclusions and Next Steps
# Summarize findings here

#%%



#%%



