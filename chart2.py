import altair as alt
from data_info import clean_data

MOY = df.groupby('MONTH')['MONTH'].agg([('N', 'count')]).reset_index().sort_values('MONTH', ascending=True)
    TOD = df.groupby('HOUR')['HOUR'].agg([('N', 'count')]).reset_index().sort_values('HOUR', ascending=True)
    type_crimes = df.groupby('TYPE')['TYPE'].agg([('N', 'count')]).reset_index().sort_values('N', ascending=False)
    type_crimes['contri'] = type_crimes['N']/sum(type_crimes['N'].values)

    crime_rate = df.groupby('YEAR')['YEAR'].agg([('N', 'count')]).reset_index().sort_values('YEAR', ascending=True)

chart1 = alt.Chart(MOY).mark_bar().encode(
        x=alt.X('MONTH'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Occurrence By Month"
    )

    chart2 = alt.Chart(TOD).mark_bar().encode(
        x=alt.X('HOUR'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Occurrence By Time of Day"
    )

    chart3 = alt.Chart(crime_rate).mark_line().encode(
        x=alt.X('YEAR:O'),
        y=alt.Y('N', title='Occurrence Count')
    ).properties(
        width=350,
        height=300, 
        title = "Crime Rate"
    )

    chart4 = alt.Chart(type_crimes).mark_bar().encode(
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