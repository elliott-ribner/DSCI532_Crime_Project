import numpy as np
import pandas as pd
import altair as alt
import os as os
# need to pip install pyproj
from pyproj import Proj

# Creating Path to read data from the repo
x = os.getcwd()
x = x[:len(x)-0]
path=x + "/Data/crimedata_csv_all_years.csv"

# Reading Vancouver City Population from 2001 to 2018
path_pop=x + "/Data/Population_trend.csv"
pop_yr = pd.read_csv(path_pop)
pop_yr = pop_yr[['YEAR', 'Population']]

# Reading each neighborhood's proportion of population to overall city's population
path_prop=x + "/Data/population_proportion.csv"
pop_prop = pd.read_csv(path_prop)

def clean_data():
    
    #alt.renderers.enable('notebook')
    alt.data_transformers.disable_max_rows()

    #mydata = pd.read_csv('~/MDS/DSCI_532_Group114_SKEC/Data/crimedata_csv_all_years.csv')
    mydata = pd.read_csv(path)
    mydata = mydata[~((mydata['X']==0) | (mydata['Y']==0) | (mydata['NEIGHBOURHOOD'].isna()))]
    mydata = mydata.drop(columns=['DAY', 'MINUTE', 'HUNDRED_BLOCK'])

    # >>>>
    # Excluding Year 2019 because the data is till Oct only whereas other years have full data
    mydata = mydata[mydata['YEAR']!=2019]
    # Relacing Stanley Park with West End because its a subset
    mydata = mydata.replace({'NEIGHBOURHOOD': 'Stanley Park'}, value = 'West End')
    # Relacing Musqueam with Marpole because its a subset
    mydata = mydata.replace({'NEIGHBOURHOOD': 'Musqueam'}, value = 'Marpole')
    mydata = mydata.replace({'NEIGHBOURHOOD': 'Central Business District'}, value = 'Downtown')
    # >>>>


    # Converting XY UTM coordinate system to Latitude & Longitude
    p = Proj(proj='utm',zone=10,ellps='WGS84', preserve_units=False)
    lon, lat = p(mydata['X'].values, mydata['Y'].values, inverse=True)
    latlon = pd.DataFrame(np.c_[lon, lat], columns=['Lon', 'Lat'])
    mydata['Lon']=latlon['Lon']
    mydata['Lat']=latlon['Lat']
    return mydata