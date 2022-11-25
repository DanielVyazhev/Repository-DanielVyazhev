import warnings
warnings.filterwarnings('ignore')
import webbrowser
import geopandas as gpd
import pandas as pd
import numpy as np
import json
import h3pandas
import folium
import osmnx as ox
from shapely import wkt
from folium.plugins import HeatMap
from shapely.geometry import Polygon


#-------------------------------Geocoding of adresses-------------------------------


# выгрузим границы Москвы из OSM
# gdf = ox.geocode_to_gdf('Москва', which_result=1) # Old Moscow + New Moscow polygon
# moscow_hex = gdf.h3.polyfill_resample(9)
#
# m = folium.Map([gdf.centroid.y, gdf.centroid.x], tiles='cartodbpositron')
#
# folium.GeoJson(gdf).add_to(m)
# folium.GeoJson(moscow_hex).add_to(m)
# folium.FitBounds([[gdf.bounds.miny[0], gdf.bounds.minx[0]],[gdf.bounds.maxy[0], gdf.bounds.maxx[0]]]).add_to(m)
# m.save(f'C:\codespace\map.html')
# webbrowser.open_new_tab(f'C:\codespace\map.html')
#
#
# new_data = pd.read_csv('new_data.csv')
# activities_list = new_data['id'].to_list()
# gdf = gpd.GeoDataFrame()
# for activity_id in activities_list:
#     df = pd.read_csv('new_data.csv'.format(activity_id))
#     line = gpd.GeoDataFrame(df[['activity_id']], index=[0], crs = CRS('EPSG:4326'), geometry=[LineString(zip(df.longitude, df.latitude))])
#     gdf = gdf.append(line)
#
# gdf.to_file(filename='geodata/cycling_routes.geojson', driver='GeoJSON')

#-------------------------------Creating Distance-------------------------------

# Distance from Moscow center
new_data = pd.read_csv('new_data.csv')
centrum = [37.619813, 55.753709]
new_data['new_coordinates'] = new_data['coordinates'].apply(lambda x: x.replace(' ', ','))
from geopy.distance import geodesic as GD
new_data['distance'] = new_data['new_coordinates'].apply(lambda x: GD(centrum, x).km)
#print(new_data.sort_values(by='distance', ascending=False))
new_data = new_data.drop(new_data[new_data['distance'] > 105].index)
# Cleaned data by distance > 105 km from Moscow center
# import seaborn as sns
# import matplotlib.pyplot as plt
# sns.histplot(new_data['distance'], bins=100)
# plt.show()
# print(new_data['distance'].head(5))
# max = new_data['distance'].max()
# min = new_data['distance'].min()
# print(max, min, max- min, (max - min) * 0.2)

#-------------------------------Creating Levels and Agregation-------------------------------

#print(top_100_streets)
top_districts = (new_data['district'].value_counts().sort_values())
#Plan:
# 1. Range streets
# 2. Range distance
# 3. Range seats
# 4. Range networks
# 5. Agregation
# 6. Trashold

# 1. Range streets
top_streets = (new_data['street'].value_counts().sort_values())
rank_streets = pd.DataFrame({'street': top_streets.index, 'range': range(1, 1977)})
#print('Rank Streets:', range_streets.head(10))
new_data['rank_streets'] = new_data['street'].apply(lambda x: rank_streets[rank_streets['street'] == x]['range'].values[0])
#print(new_data['range_streets'].head(10))
new_data['score_streets'] = new_data['rank_streets'].apply(lambda x: x / 1976 * 100)
#print(new_data['score_streets'].head(10))

# 2. Range Distance
top_distance = new_data['distance'].value_counts().sort_values()
rank_distance = pd.DataFrame({'distance': top_distance.index, 'range': range(1, 8992)})
new_data['rank_distance'] = new_data['distance'].apply(lambda x: rank_distance[rank_distance['distance'] == x]['range'].values[0])
#print('rank distance:',new_data['range_distance'].head(10))
new_data['score_distance'] = new_data['rank_distance'].apply(lambda x: x / 8991 * 100)
#print('score distance:',new_data['score_distance'].head(10))

# 3. Range Seats
agregate_seats = new_data.groupby('street')['number'].sum().sort_values()
#print('Агрегация посадки по улицам:',agregate_seats.tail(10))
# ранжировать агрегированную посадку по улице с конца
rank_agregate_seats = pd.DataFrame({'street': agregate_seats.index, 'range': range(1, 1977) })
#print(range_agregate_seats.head(10))
new_data['rank_agregate_seats'] = new_data['street'].apply(lambda x: rank_agregate_seats[rank_agregate_seats['street'] == x]['range'].values[0])
new_data['score_agregate_seats'] = new_data['rank_agregate_seats'].apply(lambda x: x / 1976 * 100)
#print(new_data['score_agregate_seats'].head(10))

# * Score inverse variable
inverse_variable = 1 / new_data['street'].value_counts()
new_data['inverse_variable'] = new_data['street'].apply(lambda x: inverse_variable[x])
rank_inverse_variable = pd.DataFrame({'street': inverse_variable.index, 'range': range(1, 1977)})
new_data['rank_inverse_variable'] = new_data['street'].apply(lambda x: rank_inverse_variable[rank_inverse_variable['street'] == x]['range'].values[0])
new_data['score_inverse_variable'] = new_data['rank_inverse_variable'].apply(lambda x: x / 1976 * 100)
#print(new_data['score_inverse_variable'].head(10))

# 4. Range Networks
networks = new_data.groupby('street')['chain'].sum().sort_values()
rank_networks = pd.DataFrame({'street': networks.index, 'range': range(1, 1977)})
new_data['rank_networks'] = new_data['street'].apply(lambda x: rank_networks[rank_networks['street'] == x]['range'].values[0])
new_data['score_networks'] = new_data['rank_networks'].apply(lambda x: x / 1976 * 100)
#print(new_data['score_networks'].head(10))

# 5. Agregation

pd.set_option('display.width', 440)
pd.set_option('display.max_columns', 18)

score_streets = 0.30
score_distance = 0.25
score_agregate_seats = 0.20
score_inverse_variable = 0.15
score_chains = 0.10

new_data['score'] = (new_data['score_streets'] * score_streets + new_data['score_distance'] * score_distance
                     + new_data['score_agregate_seats'] * score_agregate_seats + new_data['score_inverse_variable'] * score_inverse_variable
                     + new_data['score_networks'] * score_chains)


#Top 10 score
top_score = new_data.groupby('street')['score'].mean().sort_values(ascending=False)
print(new_data[['address', 'district', 'score_distance', 'score_agregate_seats', 'score_inverse_variable', 'score_networks', 'score']].head(10))
print(top_score.head(10))
# # threshold agregation by distance
new_data = new_data.drop(new_data[new_data['score_distance'] < 85].index)
top_score = new_data.groupby('street')['score'].mean().sort_values(ascending=False)
print(new_data[['address', 'district', 'score_distance', 'score_agregate_seats', 'score_inverse_variable', 'score_networks', 'score']].head(10))
print(top_score.head(10))

# Hexagons map
gdf = ox.geocode_to_gdf('Москва', which_result=1) # Old Moscow + New Moscow polygon
moscow_hex = gdf.h3.polyfill_resample(9)
#
m = folium.Map([gdf.centroid.y, gdf.centroid.x], tiles='cartodbpositron')
#
folium.GeoJson(gdf).add_to(m)
folium.GeoJson(moscow_hex).add_to(m)
folium.FitBounds([[gdf.bounds.miny[0], gdf.bounds.minx[0]],[gdf.bounds.maxy[0], gdf.bounds.maxx[0]]]).add_to(m)
m.save(f'C:\codespace\map.html')
webbrowser.open_new_tab(f'C:\codespace\map.html')

