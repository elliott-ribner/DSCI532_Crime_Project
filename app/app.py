import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import vega_datasets
import numpy as np
import data_info
import pandas as pd
import geopandas as gpd
import json


### NEW IMPORT
# See Docs here: https://dash-bootstrap-components.opensource.faculty.ai
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, assets_folder='assets', external_stylesheets=[dbc.themes.CERULEAN])
app.config['suppress_callback_exceptions'] = True

server = app.server
app.title = 'Dash app with pure Altair HTML'

import os as os
x = os.getcwd()
x = x[:len(x)-3]
# Reading Vancouver City Population from 2001 to 2018
path_pop=x + "/Data/Population_trend.csv"
pop_yr = pd.read_csv(path_pop)
pop_yr = pop_yr[['YEAR', 'Population']]
# Reading each neighborhood's proportion of population to overall city's population
path_prop=x + "/Data/population_proportion.csv"
pop_prop = pd.read_csv(path_prop)
# >>>>    


geo_json_file_loc= x + "/Data/local-area-boundary.geojson"
def open_geojson():
    with open(geo_json_file_loc) as json_data:
        d = json.load(json_data)
    return d

def get_gpd_df():
    vancouver_json = open_geojson()
    gdf = gpd.GeoDataFrame.from_features((vancouver_json))
    return gdf


def create_geo_data(gdf):
    choro_json = json.loads(gdf.to_json())
    choro_data = alt.Data(values = choro_json['features'])
    return choro_data

# mapping function based on all of the above
def gen_map_base(geodata, color_column):
    '''
        Generates Boston neighbourhoods map with building count choropleth
    '''
    # Add Base Layer
    base = alt.Chart(geodata).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=300,
        height=300
    )
    return base

def gen_map_cloro(geodata, geodata_2, color_column, tooltip):
    # Add Choropleth Layer
    choro = alt.Chart(geodata).mark_geoshape(
        fill='lightgray',
        stroke='black'
    ).encode(
        alt.Color(color_column, 
                  scale=alt.Scale(), title = "Crime Counts"),
         tooltip=tooltip
    )

    base = gen_map_base(geodata_2, color_column)
    return base+choro


def vancouver_map(df, df2):
    vancouver_map = gen_map_cloro(geodata = df, geodata_2 = df2, 
                        color_column='properties.N:Q'
                       # color_scheme='yelloworangered'
                        ,
                        tooltip = [alt.Tooltip('properties.NEIGHBOURHOOD:O', title = 'Neighbourhood'),
                                    alt.Tooltip('properties.N:Q', title = 'Crime Count')]
    )
    return vancouver_map



# >>>> Changing function to take data as an input
mydata = data_info.clean_data()
gdf = get_gpd_df()
gdf['NEIGHBOURHOOD'] = gdf['name']
gdf = gdf.drop(columns="name")
print(gdf.head())

def make_charts(type_lst=['Break and Enter Commercial'], 
                ngbrhd_lst=['Oakridge'], 
                yr_lst=['2012']):
    df = mydata[(mydata['TYPE'].isin(type_lst)) & (mydata['NEIGHBOURHOOD'].isin(ngbrhd_lst)) & (mydata['YEAR'].isin(yr_lst))]

    df2 = df.groupby(by = 'NEIGHBOURHOOD')['NEIGHBOURHOOD'].agg([('N', 'count')]).reset_index()
    gdf2 = gdf.merge(df2, on='NEIGHBOURHOOD', how='inner')

    choro_data = create_geo_data(gdf2)
    temp_chart = vancouver_map(choro_data, create_geo_data(gdf))

    MOY = df.groupby('MONTH')['MONTH'].agg([('N', 'count')]).reset_index().sort_values('MONTH', ascending=True)
    TOD = df.groupby('HOUR')['HOUR'].agg([('N', 'count')]).reset_index().sort_values('HOUR', ascending=True)
    type_crimes = df.groupby('TYPE')['TYPE'].agg([('N', 'count')]).reset_index().sort_values('N', ascending=False)
    type_crimes['contri'] = type_crimes['N']/sum(type_crimes['N'].values)

    crime_rate = df.groupby('YEAR')['YEAR'].agg([('N', 'count')]).reset_index().sort_values('YEAR', ascending=True)

    # >>>>
    # Adding population data to plot crime rate
    required_prop = sum(pop_prop[pop_prop['NEIGHBOURHOOD'].isin(ngbrhd_lst)]['proportion'].values)
    required_pop = pop_yr[pop_yr['YEAR'].isin(yr_lst)]
    required_pop['Population'] = required_pop['Population']*required_prop
    crime_rate = pd.merge(crime_rate, required_pop, how="inner", on="YEAR")
    crime_rate['rate'] = (crime_rate['N']/crime_rate['Population'])*1000
    # >>>>
    
    charts = {}
    charts[0] = temp_chart
    # charts[0] = alt.Chart(df).mark_point().encode(
    #     x=alt.X('Lon:Q', title='Longitude', scale=alt.Scale(domain=[np.min(df.Lon), np.max(df.Lon)])),
    #     y=alt.Y('Lat:Q', title='Latitude', scale=alt.Scale(domain=[np.min(df.Lat), np.max(df.Lat)])),
    #     color = 'NEIGHBOURHOOD:N'
    # ).properties(
    #     width=350,
    #     height=300
    # ).interactive()

    charts[1] = alt.Chart(MOY).mark_bar().encode(
        x=alt.X('MONTH'),
        y=alt.Y('N', title='Occurrence Count'),
        tooltip=[alt.Tooltip('N:Q', title = 'Occurrences'),
                                    alt.Tooltip('MONTH:Q', title = 'Month')]
    ).properties(
        width=350,
        height=300
    )

    charts[2] = alt.Chart(TOD).mark_bar().encode(
        x=alt.X('HOUR'),
        y=alt.Y('N', title='Occurrence Count'),
        tooltip=[alt.Tooltip('N:Q', title = 'Occurrences'),
                                    alt.Tooltip('HOUR:Q', title = 'Hour')]
    ).properties(
        width=350,
        height=300
    )

    charts[3] = alt.Chart(crime_rate).mark_line().encode(
        x=alt.X('YEAR:O'),
        y=alt.Y('rate', title='Crime Occurrences per 1000 People'),
        tooltip=[alt.Tooltip('rate:Q', title = 'Crime Rate'),
                                    alt.Tooltip('YEAR:Q', title = 'Year')]
    ).properties(
        width=350,
        height=300 
        
    )

    charts[4] = alt.Chart(type_crimes).mark_bar().encode(
        x=alt.X('TYPE', 
                axis=alt.Axis(title=""),
                sort=alt.EncodingSortField(
                    field='contri',
                    order="descending"
                )),
        y=alt.Y('contri', axis=alt.Axis(title='Contribution', format='%'),)
    ).properties(
        width=750,
        height=300
    )

    #test_dict = {'TYPE': df.TYPE.unique(), 'NEIGHBOURHOOD': df.NEIGHBOURHOOD.unique(), 'YEAR': df.YEAR.unique()}
    #return((chart0) & ((chart1 & chart2) | (chart3 & chart4)))
    return charts





jumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                #html.Img(src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Unico_Anello.png/1920px-Unico_Anello.png', 
                      #width='100px'),
                html.H1("Vancouver Neighbourhood Crime Rates", className="display-3"),
                html.P(
                    "This is an interactive visualization based on the data provided by the Vancouver Police Department (VPD)",
                    className="lead",
                ),
            ],
            fluid=True,
        )
    ],
    fluid=True,
)
###
selectors = dbc.Container([

    dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id='neighbour_dropdown',
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
                        {'label': 'Kerrisdale', 'value': 'Kerrisdale'},                
                        {'label': 'Riley Park', 'value': 'Riley Park'},
                        {'label': 'Arbutus Ridge', 'value': 'Arbutus Ridge'},
                        {'label': 'Renfrew-Collingwood', 'value': 'Renfrew-Collingwood'},
                        {'label': 'Killarney', 'value': 'Killarney'},
                        {'label': 'Dunbar-Southlands', 'value': 'Dunbar-Southlands'},
                        {'label': 'South Cambie', 'value': 'South Cambie'}
                    ],
                    value=['Central Business District', 'Fairview'],
                    multi=True,
                ),
                md=4,
            ),
           
            dbc.Col(
                    dcc.Dropdown(
                        id='crime_type_dropdown',
                        options=[
                            {'label': 'Break and Enter Commercial', 'value': 'Break and Enter Commercial'},
                            {'label': 'Break and Enter Residential/Other', 'value': 'Break and Enter Residential/Other'},
                            {'label': 'Homicide', 'value': 'Homicide'},
                            {'label': 'Mischief', 'value': 'Mischief'},
                            {'label': 'Offence Against a Person', 'value': 'Other Theft'},
                            {'label': 'Theft from Vehicle', 'value': 'Theft from Vehicle'},
                            {'label': 'Theft of Bicycle', 'value': 'Theft of Bicycle'},
                            {'label': 'Theft of Vehicle', 'value': '2010'},
                            {'label': 'Vehicle Collision or Pedestrian Struck (with Fatality)', 
                                'value': 'Vehicle Collision or Pedestrian Struck (with Fatality)'},
                            {'label': 'Vehicle Collision or Pedestrian Struck (with Injury)', 
                                'value': 'Vehicle Collision or Pedestrian Struck (with Injury)'}
                        ],
                        value=['Break and Enter Commercial','Homicide'],
                        multi=True,
                ),
                md=6,
            )
        ]
    ),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(
            id='year_slider',
            min=2003,
            max=2019,
            step=1,
            value=[2003, 2015],
            marks={
                 2003:{'label': '2003'},
                 2004:{'label': '2004'},
                 2005:{'label': '2005'},
                 2006:{'label': '2006'},
                 2008:{'label': '2007'},
                 2009:{'label': '2008'},
                 2007:{'label': '2009'},
                 2010:{'label': '2010'},
                 2011:{'label': '2011'},
                 2012:{'label': '2012'},
                 2013:{'label': '2013'},
                 2014:{'label': '2014'},
                 2015:{'label': '2015'},
                 2016:{'label': '2016'},
                 2017:{'label': '2017'},
                 2018:{'label': '2018'},
                 2019:{'label': '2019'}
    },
            )
        ]),
    ]),
    html.Br(),
    html.Br(),
])

###

content = dbc.Container([

        dbc.Row([
            dbc.Col([
                html.H2("Crimes In Vancouver"),
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot1',
                        height='560',
                        width='600',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[0].to_html()
                        ################ The magic happens here
                )

            ],
            md=6),
            dbc.Col([
                html.H2("Crime Occurrence by Month"),
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot2',
                        height='560',
                        width='500',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[1].to_html()
                        ################ The magic happens here
                )
            ],
            md=6),
        ]),

        dbc.Row([
            dbc.Col([
                html.H2("Crime Occurrence By Time of Day"),
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot3',
                        height='560',
                        width='500',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[2].to_html()
                        ################ The magic happens here
                )

            ],
            md=6),
            dbc.Col([
                html.H2("Crime Rate"),
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot4',
                        height='560',
                        width='500',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[3].to_html()
                        ################ The magic happens here
                 )
            ],
            md=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.H2("Constituents on Selected Crimes"),
                
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot5',
                        height='560',
                        width='1000',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[4].to_html()
                        ################ The magic happens here
                )

            ],
            md=12),
        ]),
    ]
)

footer = dbc.Container([dbc.Row(dbc.Col(html.P('This was made collaboratively by Chimaobi, Elliot, Kirk, and Shivam'))),
         ])

app.layout = html.Div([jumbotron,
                       selectors,
                       content,
                       footer])


@app.callback(
    dash.dependencies.Output('plot1', 'srcDoc'),
    [dash.dependencies.Input('crime_type_dropdown', 'value'),
     dash.dependencies.Input('neighbour_dropdown', 'value'),
     dash.dependencies.Input('year_slider', 'value')])
def update_plot(type_lst, ngbrhd_lst, yr_lst):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    yr_lst_temp = yr_lst

    yr_lst = []
    for year in range(yr_lst_temp[0],yr_lst_temp[1]+1):
        yr_lst.append(year)

    updated_plot = make_charts(type_lst, ngbrhd_lst, yr_lst)[0].to_html()
    return updated_plot

@app.callback(
    dash.dependencies.Output('plot2', 'srcDoc'),
    [dash.dependencies.Input('crime_type_dropdown', 'value'),
     dash.dependencies.Input('neighbour_dropdown', 'value'),
     dash.dependencies.Input('year_slider', 'value')])
def update_plot2(type_lst, ngbrhd_lst, yr_lst):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    yr_lst_temp = yr_lst

    yr_lst = []
    for year in range(yr_lst_temp[0],yr_lst_temp[1]+1):
        yr_lst.append(year)
    updated_plot = make_charts(type_lst, ngbrhd_lst, yr_lst)[1].to_html()
    return updated_plot

@app.callback(
    dash.dependencies.Output('plot3', 'srcDoc'),
    [dash.dependencies.Input('crime_type_dropdown', 'value'),
     dash.dependencies.Input('neighbour_dropdown', 'value'),
     dash.dependencies.Input('year_slider', 'value')])
def update_plot3(type_lst, ngbrhd_lst, yr_lst):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    yr_lst_temp = yr_lst

    yr_lst = []
    for year in range(yr_lst_temp[0],yr_lst_temp[1]+1):
        yr_lst.append(year)
    updated_plot = make_charts(type_lst, ngbrhd_lst, yr_lst)[2].to_html()
    return updated_plot

@app.callback(
    dash.dependencies.Output('plot4', 'srcDoc'),
    [dash.dependencies.Input('crime_type_dropdown', 'value'),
     dash.dependencies.Input('neighbour_dropdown', 'value'),
     dash.dependencies.Input('year_slider', 'value')])
def update_plot4(type_lst, ngbrhd_lst, yr_lst):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    yr_lst_temp = yr_lst

    yr_lst = []
    for year in range(yr_lst_temp[0],yr_lst_temp[1]+1):
        yr_lst.append(year)
    updated_plot = make_charts(type_lst, ngbrhd_lst, yr_lst)[3].to_html()
    return updated_plot

@app.callback(
    dash.dependencies.Output('plot5', 'srcDoc'),
    [dash.dependencies.Input('crime_type_dropdown', 'value'),
     dash.dependencies.Input('neighbour_dropdown', 'value'),
     dash.dependencies.Input('year_slider', 'value')])
def update_plot5(type_lst, ngbrhd_lst, yr_lst):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    yr_lst_temp = yr_lst

    yr_lst = []
    for year in range(yr_lst_temp[0],yr_lst_temp[1]+1):
        yr_lst.append(year)
    updated_plot = make_charts(type_lst, ngbrhd_lst, yr_lst)[4].to_html()
    return updated_plot

if __name__ == '__main__':
    app.run_server(debug=True)