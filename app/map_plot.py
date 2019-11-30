import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd
import geopandas as gpd
import json
alt.data_transformers.disable_max_rows()
# alt.data_transformers.enable('json')
#alt.data_transformers.enable('data_server')

# load geo_json file
geo_json_file_loc= '../Data/local-area-boundary.geojson'

def open_geojson():
    with open(geo_json_file_loc) as json_data:
        d = json.load(json_data)
    return d

def get_gpd_df():
    vancouver_json = open_geojson()
    gdf = gpd.GeoDataFrame.from_features((vancouver_json))
    return gdf

gdf = get_gpd_df()
# load crime data
df = pd.read_csv("../Data/crimedata_csv_all_years.csv", encoding = 'latin-1', )
df = df[["NEIGHBOURHOOD", "TYPE", 'YEAR','MONTH','HOUR']]
df['NEIGHBOURHOOD'] = df['NEIGHBOURHOOD'].str.replace("Musqueam", "Marpole",regex = True)
df['NEIGHBOURHOOD'] = df['NEIGHBOURHOOD'].str.replace("Stanley Park", "West End",regex = True)
df['TYPE'] = df['TYPE'].str.replace("Vehicle Collision or Pedestrian Struck (with Fatality)", "Vehicle Collision or Pedestrian Struck",regex = True)
df['TYPE'] = df['TYPE'].str.replace("Vehicle Collision or Pedestrian Struck (with Injury)", "Vehicle Collision or Pedestrian Struck",regex = True)


## FUNCTIONS
def chart_filter(df, year = None, month = None, neighbourhood = None, crime = None):
    filtered_df = df
    if year != None:
        if type(year) == list:
            year_list = list(range(year[0], year[1]+1))
            filtered_df = filtered_df.query('YEAR == %s' % year_list)
        else:
            filtered_df = filtered_df.query('YEAR == %s' % year)
    if month != None:
        if type(month) == list:
            month_list = list(range(month[0], month[1]+1))
            filtered_df = filtered_df.query('MONTH == %s' % month_list)
        else:
            filtered_df = filtered_df.query('MONTH == %s' % month)
    if neighbourhood != None:
        if neighbourhood == []:
            neighbourhood = None
        elif type(neighbourhood) == list:
            filtered_df = filtered_df.query('DISTRICT == %s' % neighbourhood)
        else:
            filtered_df = filtered_df.query('DISTRICT == "%s"' % neighbourhood)
    if crime != None:
        if crime == []:
            crime = None
        elif type(crime) == list:
            filtered_df = filtered_df.query('OFFENSE_CODE_GROUP == %s' % crime)
        else:
            filtered_df = filtered_df.query('OFFENSE_CODE_GROUP == "%s"' % crime)       
    return filtered_df

# determine whether the input year is single value or not
def year_filter(year = None):
    if year[0] == year[1]:
        single_year = True
    else:
        single_year = False
    return single_year

# use the filtered dataframe to create the map
# create the geo pandas merged dataframe
def create_merged_gdf(df, gdf, neighbourhood):
    df = df.groupby(by = 'NEIGHBOURHOOD').agg("count")
    if neighbourhood != None:
        neighbourhood = list(neighbourhood)
        for index_label, row_series in df.iterrows():
        # For each row update the 'Bonus' value to it's double
            if index_label not in neighbourhood:
                df.at[index_label , 'YEAR'] = None
    gdf = gdf.merge(df, left_on='name', right_on='NEIGHBOURHOOD', how='inner')
    return gdf

def create_geo_data(gdf):
    choro_json = json.loads(gdf.to_json())
    choro_data = alt.Data(values = choro_json['features'])
    return choro_data

# mapping function based on all of the above
def gen_map(geodata, color_column, title, tooltip):
    '''
        Generates Boston neighbourhoods map with building count choropleth
    '''
    # Add Base Layer
    base = alt.Chart(geodata, title = title).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=300,
        height=300
    )
    # Add Choropleth Layer
    choro = alt.Chart(geodata).mark_geoshape(
        fill='lightgray',
        stroke='black'
    ).encode(
        alt.Color(color_column, 
                  type='quantitative', 
                  scale=alt.Scale(),
                  title = "Crime Counts"),
         tooltip=tooltip
    )
    return base + choro

# create plot functions

def vancouver_map(df):
    vancouver_map = gen_map(geodata = df, 
                        color_column='properties.YEAR', 
                       # color_scheme='yelloworangered',
                        title = "Crime Counts by Neighbourhood",
                        tooltip = [alt.Tooltip('properties.Name:O', title = 'Neighbourhood'),
                                    alt.Tooltip('properties.YEAR:Q', title = 'Crime Count')]
    ).configure_legend(labelFontSize=14, titleFontSize=16)
    return vancouver_map

# set theme
def mds_special():
        font = "Arial"
        axisColor = "#000000"
        gridColor = "#DEDDDD"
        return {
            "config": {
                "title": {
                    "fontSize": 24,
                    "font": font,
                    "anchor": "start", # equivalent of left-aligned.
                    "fontColor": "#000000"
                },
                'view': {
                    "height": 300, 
                    "width": 400
                },
                "axisX": {
                    "domain": True,
                    #"domainColor": axisColor,
                    "gridColor": gridColor,
                    "domainWidth": 1,
                    "grid": False,
                    "labelFont": font,
                    "labelFontSize": 12,
                    "labelAngle": 0, 
                    "tickColor": axisColor,
                    "tickSize": 5, # default, including it just to show you can change it
                    "titleFont": font,
                    "titleFontSize": 16,
                    "titlePadding": 10, # guessing, not specified in styleguide
                    "title": "X Axis Title (units)", 
                },
                "axisY": {
                    "domain": False,
                    "grid": True,
                    "gridColor": gridColor,
                    "gridWidth": 1,
                    "labelFont": font,
                    "labelFontSize": 14,
                    "labelAngle": 0, 
                    #"ticks": False, # even if you don't have a "domain" you need to turn these off.
                    "titleFont": font,
                    "titleFontSize": 16,
                    "titlePadding": 10, # guessing, not specified in styleguide
                    "title": "Y Axis Title (units)", 
                    # titles are by default vertical left of axis so we need to hack this 
                    #"titleAngle": 0, # horizontal
                    #"titleY": -10, # move it up
                    #"titleX": 18, # move it to the right so it aligns with the labels 
                },
            }
                }

# register the custom theme under a chosen name
alt.themes.register('mds_special', mds_special)

# enable the newly registered theme
alt.themes.enable('mds_special')

## wrap all the other functions
def make_choro_plot(df, gdf, year = None, month = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, month = month, crime = crime)
    gdf = create_merged_gdf(df, gdf, neighbourhood = neighbourhood)
    choro_data = create_geo_data(gdf)
    return  vancouver_map(choro_data)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = 'Vancouver Crime Dashboard'

# colour dictionary
colors = {"white": "#ffffff",
          "light_grey": "#d2d7df",
          "ubc_blue": "#082145"
          }

app.layout = html.Div(style={'backgroundColor': colors['light_grey']}, children = [

    # HEADER
    html.Div(className = 'row', style = {'backgroundColor': colors["ubc_blue"], "padding" : 10}, children = [
        html.H2('Vancouver Crime Dashboard', style={'color' : colors["white"]})
    ]),
    
    # BODY
    html.Div(className = "row", children = [

         #SIDE BAR
        html.Div(className = "two columns", style = {'padding': 20}, children= [
            html.P("Filter by Year"),
            dcc.RangeSlider(
                    id = 'year-slider',
                    min=2015,
                    max=2018,
                    step=1,
                    marks={
                        2015: '2015',
                        2016: '2016',
                        2017: '2017',
                        2018: '2018'
                        },
                    value=[2015,2018],
            ),
            html.Br(),
            html.P("Filter by Month"),
            dcc.RangeSlider(
                id = 'month-slider',
                min=1,
                max=12,
                step=1,
                marks={
                    1: 'Jan',
                    2: '',
                    3: '',
                    4: '',
                    5: '',
                    6: 'June',
                    7: '',
                    8: '',
                    9: '',
                    10: '',
                    11: '',
                    12: 'Dec'
                    },
                value=[1,12],
                ),

            

            html.Br(),
            html.P("Filter by Neighbourhood"),
            dcc.Dropdown(
                id = 'neighbourhood-dropdown',
                    options=[
                        {'label': 'Oakridge', 'value': 'Oakridge'},
                        {'label': 'Fairview', 'value': 'Fairview'},
                        {'label': 'West End', 'value': 'West End'},
                        {'label': 'Central Business District', 'value': 'Central Business District'},
                        {'label': 'Hastings-Sunrise', 'value': 'Hastings-Sunrise'},
                        {'label': 'Strathcona', 'value': 'Strathcona'},
                        {'label': 'Grandview-Woodland', 'value': 'Grandview-Woodland'},
                        {'label': 'Kitsilano', 'value': 'Kitsilano'},                
                        {'label': 'Kensington-Cedar Cottage', 'value': 'Kensington-Cedar Cottage'},                
                        {'label': 'Sunset', 'value': 'Sunset'},                
                        {'label': 'Mount Pleasant', 'value': 'Mount Pleasant'} ,
                        {'label': 'Shaughnessy', 'value': 'Shaughnessy'},
                        {'label': 'Marpole', 'value': 'Marpole'},                
                        {'label': 'West Point Grey', 'value': 'West Point Grey'},                
                        {'label': 'Victoria-Fraserview', 'value': 'Victoria-Fraserview'},                
                        {'label': 'Riley Park', 'value': 'Riley Park'},
                        {'label': 'Arbutus Ridge', 'value': 'Arbutus Ridge'},
                        {'label': 'Renfrew-Collingwood', 'value': 'Renfrew-Collingwood'},
                        {'label': 'Killarney', 'value': 'Killarney'},
                        {'label': 'Dunbar-Southlands', 'value': 'Dunbar-Southlands'},
                        {'label': 'South Cambie', 'value': 'South Cambie'}



                    ],
                    value=None, style=dict(width='100%'),
                    multi=True          
                    ),

            html.Br(),
            html.P("Filter by Crime"),
            dcc.Dropdown(
                id = 'crime-dropdown',
                    options=[
                        {'label': 'Break and Enter Commercial', 'value': 'Break and Enter Commercial'} ,
                        {'label': 'Break and Enter Residential/Other', 'value': 'Break and Enter Residential/Other'} ,
                        {'label': 'Homicide', 'value': 'Homicide'} ,
                        {'label': 'Mischief', 'value': 'Mischief'} ,
                        {'label': 'Offence Against a Person', 'value': 'Offence Against a Person'} ,
                        {'label': 'Other Theft', 'value': 'Other Theft'} ,
                        {'label': 'Theft from Vehicle', 'value': 'Theft from Vehicle'} ,
                        {'label': 'Theft of Bicycle', 'value': 'Theft of Bicycle'} ,
                        {'label': 'Theft of Vehicle', 'value': 'Theft of Vehicle'} ,
                        {'label': 'Vehicle Collision or Pedestrian Struck', 'value': 'Vehicle Collision or Pedestrian Struck'} 
                    ],
                    value=None, style=dict(width='100%'),
                    multi=True
                    ),
        ]),
            # MAIN PLOTS
            html.Div(className = "ten columns", style = {"backgroundColor": colors['white'], "padding": 20}, children=[

                html.Iframe(
                    sandbox='allow-scripts',
                    id='choro-plot',
                    height='800',
                    width='800',
                    style={'border-width': '0px'},
                    )

            ])
    
        ])
])

@app.callback(
        dash.dependencies.Output('choro-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('month-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_choro_plot(year_value, month_value, neighbourhood_value, crime_value):
    return make_choro_plot(df, gdf, year = year_value, month = month_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()

if __name__ == '__main__':
    app.run_server(debug=True)