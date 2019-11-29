import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import vega_datasets
import numpy as np
import data_info

### NEW IMPORT
# See Docs here: https://dash-bootstrap-components.opensource.faculty.ai
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, assets_folder='assets', external_stylesheets=[dbc.themes.CERULEAN])
app.config['suppress_callback_exceptions'] = True

server = app.server
app.title = 'Dash app with pure Altair HTML'



def make_charts(type_lst=['Break and Enter Commercial'], ngbrhd_lst=['Oakridge'], yr_lst=['2012']):
    mydata = data_info.clean_data()
    df = mydata[(mydata['TYPE'].isin(type_lst)) & (mydata['NEIGHBOURHOOD'].isin(ngbrhd_lst)) & (mydata['YEAR'].isin(yr_lst))]
    
    MOY = df.groupby('MONTH')['MONTH'].agg([('N', 'count')]).reset_index().sort_values('MONTH', ascending=True)
    TOD = df.groupby('HOUR')['HOUR'].agg([('N', 'count')]).reset_index().sort_values('HOUR', ascending=True)
    type_crimes = df.groupby('TYPE')['TYPE'].agg([('N', 'count')]).reset_index().sort_values('N', ascending=False)
    type_crimes['contri'] = type_crimes['N']/sum(type_crimes['N'].values)

    crime_rate = df.groupby('YEAR')['YEAR'].agg([('N', 'count')]).reset_index().sort_values('YEAR', ascending=True)

    charts = {}
    charts[0] = alt.Chart(df).mark_point().encode(
        x=alt.X('Lon:Q', title='Longitude', scale=alt.Scale(domain=[np.min(df.Lon), np.max(df.Lon)])),
        y=alt.Y('Lat:Q', title='Latitude', scale=alt.Scale(domain=[np.min(df.Lat), np.max(df.Lat)])),
        color = 'NEIGHBOURHOOD:N'
    ).properties(
        width=700,
        height=400, 
        title = "Crimes In Vancouver"
    ).interactive()

    charts[1] = alt.Chart(MOY).mark_bar().encode(
        x=alt.X('MONTH'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Occurrence By Month"
    )

    charts[2] = alt.Chart(TOD).mark_bar().encode(
        x=alt.X('HOUR'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Occurrence By Time of Day"
    )

    charts[3] = alt.Chart(crime_rate).mark_line().encode(
        x=alt.X('YEAR:O'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Rate"
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
        title="Constituents on Selected Crimes",
        width=350,
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
                    "This is an interactive visualization app based on the data provided by the Vancouver Police Department (VPD)",
                    className="lead",
                ),
            ],
            fluid=True,
        )
    ],
    fluid=True,
)

#logo = dbc.Row(dbc.Col(html.Img(src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Unico_Anello.png/1920px-Unico_Anello.png', 
                      #width='15%'), width=4))

content = dbc.Container([

        dbc.Row([
            dbc.Col([
                html.H2("Section 1"),
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot1',
                        height='560',
                        width='500',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[0].to_html()
                        ################ The magic happens here
                )

            ],
            md=6),
            dbc.Col([
                html.H2("Section 2"),
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
                html.H2("Section 3"),
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
                html.H2("Section 4"),
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
                html.H2("Section 1"),
                
                html.Iframe(
                        sandbox='allow-scripts',
                        id='plot5',
                        height='560',
                        width='500',
                        style={'border-width': '0'},
                        ################ The magic happens here
                        srcDoc=make_charts()[4].to_html()
                        ################ The magic happens here
                )

            ]),
        ]),
    ]
)

footer = dbc.Container([dbc.Row(dbc.Col(html.P('This Dash app was made collaboratively by Chimaobi, Elliot, Kirk, and Shivam'))),
         ])

app.layout = html.Div([jumbotron,
                       content,
                       footer])


@app.callback(
    dash.dependencies.Output('plot', 'srcDoc'),
    [dash.dependencies.Input('dd-chart-x', 'value'),
     dash.dependencies.Input('dd-chart-y', 'value')])
def update_plot(xaxis_column_name,
                yaxis_column_name):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = make_plot(xaxis_column_name,
                             yaxis_column_name).to_html()
    return updated_plot

if __name__ == '__main__':
    app.run_server(debug=True)