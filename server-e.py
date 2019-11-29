import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd
import vega_datasets
from pyproj import Proj
import numpy as np

app = dash.Dash(__name__, assets_folder='assets')
server = app.server
app.title = 'Dash app with pure Altair HTML'


## DATA WRANGLING AND GATHERING

ngbrhd_lst = ['Central Business District', 'West End', 'Fairview', 'Mount Pleasant']
type_lst = ['Mischief', 'Break and Enter Residential/Other', 'Theft of Vehicle']
yr_lst = list(np.arange(2013,2018,1))

crime_data = pd.read_csv('Data/crimedata_csv_all_years.csv')

crime_data = crime_data[~((crime_data['X']==0) | (crime_data['Y']==0) | (crime_data['NEIGHBOURHOOD'].isna()))]
crime_data = crime_data.drop(columns=['DAY', 'MINUTE', 'HUNDRED_BLOCK'])

# Converting XY UTM coordinate system to Latitude & Longitude
p = Proj(proj='utm',zone=10,ellps='WGS84', preserve_units=False)
lon, lat = p(crime_data['X'].values, crime_data['Y'].values, inverse=True)
latlon = pd.DataFrame(np.c_[lon, lat], columns=['Lon', 'Lat'])
crime_data['Lon']=latlon['Lon']
crime_data['Lat']=latlon['Lat']

df = crime_data[(crime_data['TYPE'].isin(type_lst)) & (crime_data['NEIGHBOURHOOD'].isin(ngbrhd_lst)) & (crime_data['YEAR'].isin(yr_lst))]
    
MOY = df.groupby('MONTH')['MONTH'].agg([('N', 'count')]).reset_index().sort_values('MONTH', ascending=True)
TOD = df.groupby('HOUR')['HOUR'].agg([('N', 'count')]).reset_index().sort_values('HOUR', ascending=True)
type_crimes = df.groupby('TYPE')['TYPE'].agg([('N', 'count')]).reset_index().sort_values('N', ascending=False)
type_crimes['contri'] = type_crimes['N']/sum(type_crimes['N'].values)

crime_rate = df.groupby('YEAR')['YEAR'].agg([('N', 'count')]).reset_index().sort_values('YEAR', ascending=True)

## END DATA WRANGLING AND GATHERING

def make_year_chart(neighborhood = 'All'):
    filteredDf = crime_rate
    if (neighborhood != 'All'):
        filteredDf = df[df['NEIGHBOURHOOD'] == neighborhood].groupby('YEAR')['YEAR'].agg([('N', 'count')]).reset_index().sort_values('YEAR', ascending=True)
    year_chart = alt.Chart(filteredDf).mark_line().encode(
        x=alt.X('YEAR:O'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Rate"
    )
    return year_chart

def make_month_chart():
    month_chart = alt.Chart(TOD).mark_bar().encode(
        x=alt.X('HOUR'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Occurrence By Time of Day"
    )
    return month_chart


jumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.Img(src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Unico_Anello.png/1920px-Unico_Anello.png', 
                      width='100px'),
                html.H1("Vancouver crime data", className="display-3"),
                html.P(
                    "This is a dashboard for crime data in Vacouver",
                    className="lead",
                ),
            ],
            fluid=True,
        )
    ],
    fluid=True,
)


selectors = dbc.Container([
    dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id='crime-type-dropdown',
                    options=[
                        {'label': 'All Neigborhoods', 'value': 'All'},
                        {'label': 'Central Business District', 'value': 'Central Business District'},
                        {'label': 'West End', 'value': 'West End'},
                        {'label': 'Fairview', 'value': 'Fairview'},
                        {'label': 'Mount Pleasant', 'value': 'Mount Pleasant'}
                    ],
                    value='All'
                ),
            )
        ]
    )
])

content = dbc.Container([
    dbc.Row(
        [
            dbc.Col(
                html.Iframe(
                            sandbox='allow-scripts',
                            id='year_chart',
                            height='470',
                            width='655',
                            style={'border-width': '0'},
                            ################ The magic happens here
                            srcDoc=make_year_chart().to_html()
                            ################ The magic happens here
                        ),
            ),
            dbc.Col(
                html.Iframe(
                            sandbox='allow-scripts',
                            id='month_chart',
                            height='470',
                            width='655',
                            style={'border-width': '0'},
                            ################ The magic happens here
                            srcDoc=make_month_chart().to_html()
                            ################ The magic happens here
                        ),
            )
        ]
    )
])


footer = dbc.Container([
            dbc.Row(
                dbc.Col(
                    html.P('This app was made for data viz 2 by group 114')
                )
            )
         ]
)

app.layout = html.Div([jumbotron, selectors, content, footer])


@app.callback(
    dash.dependencies.Output('year_chart', 'srcDoc'),
    [dash.dependencies.Input('crime-type-dropdown', 'value')])
def update_plot(neighborhood):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = make_year_chart(neighborhood).to_html()
    return updated_plot
if __name__ == '__main__':
    app.run_server(debug=True)