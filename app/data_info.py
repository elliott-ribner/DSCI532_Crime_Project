import numpy as np
import pandas as pd
import altair as alt

# need to pip install pyproj
from pyproj import Proj


def clean_data():
    
    #alt.renderers.enable('notebook')
    alt.data_transformers.disable_max_rows()

    mydata = pd.read_csv('~/MDS/DSCI_532_Group114_SKEC/Data/crimedata_csv_all_years.csv')
    
    mydata = mydata[~((mydata['X']==0) | (mydata['Y']==0) | (mydata['NEIGHBOURHOOD'].isna()))]
    mydata = mydata.drop(columns=['DAY', 'MINUTE', 'HUNDRED_BLOCK'])

    # Converting XY UTM coordinate system to Latitude & Longitude
    p = Proj(proj='utm',zone=10,ellps='WGS84', preserve_units=False)
    lon, lat = p(mydata['X'].values, mydata['Y'].values, inverse=True)
    latlon = pd.DataFrame(np.c_[lon, lat], columns=['Lon', 'Lat'])
    mydata['Lon']=latlon['Lon']
    mydata['Lat']=latlon['Lat']
    return mydata