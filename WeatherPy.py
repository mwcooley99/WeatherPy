#%% [markdown]
# # Introduction
# Do temperatures increase as we get closer to the equator? In this notebook we look at a sample of random cities distributed accross latitudes and see if there is a correlation between different latitudes and the observable weather.
#%% [markdown]
#  ### Imports
#  Import libraries and write settings here.

#%%
# Data manipulation
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np

# Options for pandas
pd.options.display.max_columns = 50
pd.options.display.max_rows = 30

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


#%%
get_ipython().run_line_magic('config', 'IPCompleter.greedy = True')

#%% [markdown]
#  # Analysis/Modeling
#  Do work here
#%% [markdown]
#  ### Create a uniformly distributed DataFrame of cities across Latitudes and Longitudes

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
# Pull the api data and create a json file of it so we don't have to call the API everytime
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
            print(f'Adding weather data for city {idx}: {city}')
            weather_data.append(response.json()['list'][0])
        else:
            print(f'{city} not found...' )
    # Write to file
    with open('assets/weather_data.json', 'w') as json_file:
        json.dump(weather_data, json_file)


#%%
# Load json into DataFrame for analysis and write it a file
weather_df = json_normalize(weather_data)
weather_df.to_csv('output/weather_data.csv', index=False)

#%% [markdown]
#  # Results
#  Show graphs and stats here

#%%
plt.style.use('ggplot')
args = {'c': 'coord.lon', 'cmap': 'plasma'}


#%%
# Plot the Temperature
fig, ax1 = plt.subplots(figsize=(12,8))

weather_df.plot(x='coord.lat', y='main.temp', kind='scatter', 
                ax=ax1, title='Temperature', **args)
ax1.set_xlabel('Latitude')
ax1.set_ylabel('Temperature (F)')

fig.savefig('output/temperature.png')
fig.tight_layout()


#%%
# Plot the Humidity
fig, ax2 = plt.subplots(figsize=(12,8))

weather_df.plot(x='coord.lat', y='main.humidity', kind='scatter', 
                ax=ax2, title='Humidity', **args)
ax2.set_xlabel('Latitude')
ax2.set_ylabel('% Humidity')

fig.savefig('output/humidity.png')
fig.tight_layout()


#%%
# Plot of the Cloudiness
fig, ax3 = plt.subplots(figsize=(12,8))

weather_df.plot(x='coord.lat', y='clouds.all', kind='scatter', ax=ax3, title='Cloudiness', **args)
ax3.set_xlabel('Latidude')
ax3.set_ylabel('% Cloudiness')

fig.savefig('output/cloudiness.png')
fig.tight_layout()


#%%
# Plot of the Wind Speed
fig, ax4 = plt.subplots(figsize=(10,8))

weather_df.plot(x='coord.lat', y='wind.speed', kind='scatter', 
                ax=ax4, title='Wind Speed', **args)
ax4.set_xlabel('Latitude')
ax4.set_ylabel('Wind Speed (mph)')

fig.tight_layout()
fig.savefig('output/wind_speed.png')

#%% [markdown]
#  # Conclusions and Next Steps
#  Summarize findings here
#  1. From the nice bell-shaped curve in the temperature plot, we can see that the temperature does indeed increase as we approach the equator
#  2. We can also note that there is clearly no correlation between Humidity, Cloudiness, or Windspeed compared with respect to Latitude.
#  3. Suprisingly the fact that the measuerments were taken from differnt times of day (they were all taken at roughly the same moment, but at different longitudes), seemed to have little impact on the temperatures being warmer, the closer you get to the equator.
# 
# 

