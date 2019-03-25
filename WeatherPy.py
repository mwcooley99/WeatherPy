#%% [markdown]
# # Introduction
# State notebook purpose here
#%% [markdown]
# ### Imports
# Import libraries and write settings here.

#%%
# Data manipulation
import pandas as pd
from pandas.io.json import json_normalize
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
import time

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
city_name = "London,uk"
params = {'q': city_name, 'APPID': api_key, 'units': 'imperial'}
response = requests.get(base_url, params=params)
print(json.dumps(response.json(), indent=4, sort_keys=True))
type(response.status_code)
#%%
# Method to use with DataFrame to find the closest cities.
def get_nearest_city(coor):
    city = citipy.nearest_city(coor['Latitude'], coor['Longitude'])
    return city.city_name + ',' + city.country_code

#%%
if not 'city' in city_df.columns:
    print('finding closests cities')
    city_df['city'] = city_df.apply(get_nearest_city, axis=1)
    pd.to_pickle(city_df, 'assets/city_df')
city_df.head()
#%%
# Check for Nan cities and remove duplicates
num_of_na = len(city_df[city_df['city'].isna()])
city_df = city_df.drop_duplicates(subset='city')
print(f'There were {num_of_na} cities not found')
print(city_df.shape)

#%%
# Pull the api data and create a json file of it so I don't have to do
# an API all every time
try: 
    with open('assets/weather_data.json') as json_data:
        weather_data = json.load(json_data)
    print('File Found!')
except OSError:
    weather_data = []
    params = params = {'q': '', 'APPID': api_key, 'units': 'imperial'}
    for idx, city in enumerate(city_df['city'].values):
        params['q'] = city
        response = requests.get(base_url, params=params)
        while response.status_code != 200:
            print(f'Request for {city} failed with code {response.status_code}. Trying again')
            time.sleep(5)
        if response.json()['count'] > 0:
            print(f'Adding weather data for {city}')
            weather_data.append(response.json()['list'][0])
        else:
            print(f'{city} not found...' )
    # Write to file
    with open('assets/weather_data.json', 'w') as json_file:
        json.dump(weather_data, json_file)
    

#%%
# Load json into DataFrame for analysis
weather_df = json_normalize(weather_data)
#%%
weather_df = weather_df.sort_values(by='coord.lat')
weather_df.info()
#%%
# Plot the figures
fig, ax_array = plt.subplots(nrows=2, ncols=2, figsize=(10,8))
ax1 = ax_array[0][0]
ax1.set_xlabel('Latitude')
ax1.set_ylabel('Temperature (F)')

ax2 = ax_array[0][1]
ax2.set_xlabel('Latitude')
ax2.set_ylabel('% Humidity')

ax3 = ax_array[1][0]
ax3.set_xlabel('Latidude')
ax3.set_ylabel('% Cloudiness')

ax4 = ax_array[1][1]
ax4.set_xlabel('Latitude')
ax4.set_ylabel('Wind Speed (mph)')

weather_df.plot(x='coord.lat', y='main.temp', kind='scatter', ax=ax1, title='Temperature')
weather_df.plot(x='coord.lat', y='main.humidity', kind='scatter', ax=ax2, title='Humidity')
weather_df.plot(x='coord.lat', y='clouds.all', kind='scatter', ax=ax3, title='Cloudiness', )
weather_df.plot(x='coord.lat', y='wind.speed', kind='scatter', ax=ax4, title='Wind Speed')
fig.tight_layout()
#%% [markdown]
# # Results
# Show graphs and stats here
#%% [markdown]
# # Conclusions and Next Steps
# Summarize findings here

#%%


#%%



#%%



