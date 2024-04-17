import requests
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px 
import dash_bootstrap_components as dbc

# generate variables and constants
election_years = [year for year in range(2009, 2022, 3)]
# Mapping each election year to its corresponding dataframe


def distribute_alliance_votes(df, alliances):
    # ensure that party columns exist in the dataframe, add them if the do not
    all_parties = set(party for parties in alliances.values() for party in parties)
    for party in all_parties:
        if party not in df.columns:
            df[party] = 0

    # distribute the votes from each alliance to the respective parties
    for alliance, parties in alliances.items():
        if alliance in df.columns:
            split_votes = df[alliance] / len(parties)
            for party in parties:
                df[party] += split_votes

    # optionally remove the alliance columns
    df.drop(columns = list(alliances.keys()), inplace = True, errors = 'ignore')

    return df


main_parties = {
    'PAN': 'PAN',
    'PRI': 'PRI',
    'PRD': 'PRD',
    'PVEM': 'PVEM',
    'PT': 'PT',
    'MC': 'MC',
    'MORENA': 'MORENA',
    'NVA_ALIANZA': 'NVA_ALIANZA',
    'PSD': ['PSD'],
    'PRIMERO_MEXICO': ['PRIMERO_MEXICO'],
    'SALVEMOS_MEXICO': ['SALVEMOS_MEXICO'],
    'PH': ['PH'],
    'ES': ['ES'],
    'NA': ['NA'],
    'PES': ['PES'],
    'RSP': ['RSP'],
    'FXM': ['FXM'],
    # Add more as needed for each unique party or alliance...
}

alliance_votes_mapping = {
    'PAN_NVA_ALIANZA': ['PAN', 'NVA_ALIANZA'],
    'PAN_PRD': ['PAN', 'PRD'],
    'PRI_PVEM': ['PRI', 'PVEM'],
    'PRI_NA': ['PRI', 'NA'],
    'PRI_PVEM_NA': ['PRI', 'PVEM', 'NA'],
    'PAN_PRI_PRD': ['PAN', 'PRI', 'PRD'],
    'PAN_PRI': ['PAN', 'PRI'],
    'PRI_PRD': ['PRI', 'PRD'],
    'PRD_PT': ['PRD', 'PT'],
    'PVEM_NA': ['PVEM', 'NA'],
    'PVEM_PT': ['PVEM', 'PT'],
    'PT_ES': ['PT', 'ES'],
    'PRD_PT_MC': ['PRD', 'PT', 'MC'],
    'PRD_MC': ['PRD', 'MC'],
    'PT_MC': ['PT', 'MC'],
    'PAN_PRD_MC': ['PAN', 'PRD', 'MC'],
    'PAN_MC': ['PAN', 'MC'],
    'MORENA_ES': ['MORENA', 'ES'],
    'PT_MORENA_ES': ['PT', 'MORENA', 'ES'],
    'PT_MORENA': ['PT', 'MORENA'],
    'PVEM_PT_MORENA': ['PVEM', 'PT', 'MORENA'],
    'PVEM_MORENA': ['PVEM', 'MORENA'],
    # Add any other specific alliances as needed
}

# load data

# URL of the GeoJSON file on GitHub
geojson_url = 'https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/qroo_geojson_2022.json'

# Fetch the GeoJSON data
response = requests.get(geojson_url)
geojson_data = response.json() if response.status_code == 200 else None


df_ln_sx_qroo = pd.read_csv('https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_lista_nominal_sexo.csv')

df_ln_age_qroo = pd.read_csv('https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_lista_nominal_edad.csv')

csv_urls = [
    'https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_results_2009.csv',
    'https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_results_2012.csv',
    'https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_results_2015.csv',
    'https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_results_2018.csv',
    'https://raw.githubusercontent.com/vflores-io/elections_dash/main/data/cleaned_results_2021.csv'
    # Add more URLs as needed
]

# Load each CSV file into a DataFrame 
df_re_2009_qroo = pd.read_csv(csv_urls[0])
df_re_2012_qroo = pd.read_csv(csv_urls[1])
df_re_2015_qroo = pd.read_csv(csv_urls[2])
df_re_2018_qroo = pd.read_csv(csv_urls[3])
df_re_2021_qroo = pd.read_csv(csv_urls[4])

df_re_2009_qroo = distribute_alliance_votes(df_re_2009_qroo, alliance_votes_mapping)
df_re_2012_qroo = distribute_alliance_votes(df_re_2012_qroo, alliance_votes_mapping)
df_re_2015_qroo = distribute_alliance_votes(df_re_2015_qroo, alliance_votes_mapping)
df_re_2018_qroo = distribute_alliance_votes(df_re_2018_qroo, alliance_votes_mapping)
df_re_2021_qroo = distribute_alliance_votes(df_re_2021_qroo, alliance_votes_mapping)

df_re_all_years = [df_re_2009_qroo, df_re_2012_qroo, df_re_2015_qroo, df_re_2018_qroo, df_re_2021_qroo]

df_dict = {
        2009: df_re_2009_qroo,
        2012: df_re_2012_qroo,
        2015: df_re_2015_qroo,
        2018: df_re_2018_qroo,
        2021: df_re_2021_qroo,
    }

def create_total_bar_plot(df):

    # group data

    df_ln_qroo_totals = df.groupby(['Nombre Municipio'])[['Lista Hombres', 'Lista Mujeres', 'Lista Nominal']].sum().reset_index()

    fig_bar_totals = px.bar(
    df_ln_qroo_totals,
    x='Nombre Municipio', 
    y=['Lista Hombres','Lista Mujeres'],
    labels = {'value': 'Lista Nominal',
            'variable': ''}, 
    title="Lista Nominal por Municipio",
    color_discrete_sequence=px.colors.qualitative.Dark24
    )

    # make a dictionary for abbreviated municipality names

    abb_mun_dict = {
        'BACALAR': 'BCL',
        'BENITO JUAREZ': 'BJ',
        'COZUMEL': 'CZ',
        'FELIPE CARRILLO PUERTO': 'FCP',
        'ISLA MUJERES': 'IM',
        'JOSE MARIA MORELOS': 'JMM',
        'LAZARO CARDENAS': 'LC',
        'OTHON P. BLANCO': 'OPB',
        'PUERTO MORELOS': 'PM',
        'SOLIDARIDAD': 'SLD',
        'TULUM': 'TLM'
    }

    fig_bar_totals.update_layout(
        xaxis = dict(
            tickvals = df_ln_qroo_totals['Nombre Municipio'],  # Original names
            ticktext = [abb_mun_dict.get(name, name) for name in  df_ln_qroo_totals['Nombre Municipio']]  # Abbreviated names
        ),
        yaxis = dict(title = 'Lista Nominal'),
        plot_bgcolor = 'rgba(0,0,0,0)', # transparent background
        uniformtext_minsize = 8,  # ensure text size is legible
        uniformtext_mode = 'hide', # hide text if it doesn't fit
    )

    fig_bar_totals.update_traces(
        hoverinfo='x+y',  # Show the municipio name and the count on hover
        hovertemplate="<b>%{x}</b><br>Total: %{y}<extra></extra>"  # Custom hover template
    )

    return fig_bar_totals

def create_total_choropleth(df, geojson):
    
    df_ln_qroo_totals = df.groupby(['Nombre Municipio'])[['Lista Hombres', 'Lista Mujeres', 'Lista Nominal']].sum().reset_index()

    fig_choropleth_totals = px.choropleth(df_ln_qroo_totals, 
                                geojson=geojson, 
                                locations='Nombre Municipio', 
                                color='Lista Nominal',
                                featureidkey="properties.NOMGEO",  # Adjust based on your GeoJSON properties
                                projection="mercator",
                                color_continuous_scale="Portland",
                                title="Lista Nominal por Municipio")
    fig_choropleth_totals.update_geos(fitbounds="locations", visible=False)
    
    return fig_choropleth_totals


def create_age_choropleth(df, geojson):
    # Aggregate data by MUNICIPIO
    df_grouped = df.groupby('MUNICIPIO').sum().reset_index()

    # Determine the predominant age range for each municipality
    age_groups = df_grouped.columns[11:]

    df_grouped['Rango de Edad Predominante'] = df_grouped[age_groups].idxmax(axis=1)

    # when summing, pandas also concatenates the strings in "NOMBRE ENTIDAD"
    # so do some housekeeping
    df_grouped.drop(columns=['NOMBRE ENTIDAD'])

    # Assuming `geojson` is your GeoJSON object for the municipalities
    fig = px.choropleth(
        df_grouped,
        geojson=geojson,
        locations='MUNICIPIO',
        color='Rango de Edad Predominante',
        featureidkey="properties.NOMGEO",
        color_continuous_scale=px.colors.sequential.Plasma,
        projection="mercator",
        title="Rango de Edad y Genero Predominantes en la Lista Nominal Por Municipio"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    return fig


def create_gender_proportion_choropleth(df, geojson_data):
    # Aggregate data by MUNICIPIO if not already aggregated
    df_grouped = df.groupby('Nombre Municipio').sum().reset_index()

    # Calculate the percentage of women registered voters
    df_grouped['Porcentaje Mujeres'] = (df_grouped['Lista Mujeres'] / df_grouped['Lista Nominal']) * 100

    # Assuming `geojson` is your GeoJSON object for the municipalities
    fig = px.choropleth(
        df_grouped,
        geojson=geojson_data,
        locations='Nombre Municipio',
        color='Porcentaje Mujeres',
        featureidkey="properties.NOMGEO",
        color_continuous_scale=px.colors.sequential.Plasma,
        projection="mercator",
        title="Porcentaje de Mujeres en la Lista Nominal"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    return fig


def create_winning_party_per_year_choropleth(selected_year, geojson, main_parties, df_dict):
    # This function now handles a single year's DataFrame and generates a choropleth map for that year.
    
    df_year = df_dict[selected_year]

    winning_party_by_municipality = {}
    
    for municipality in df_year['MUNICIPIO'].unique():
        votes_by_party = {main_party: 0 for main_party in main_parties}
        for party in main_parties:
            if party in df_year.columns:
                votes_by_party[party] += df_year.loc[df_year['MUNICIPIO'] == municipality, party].sum()

    
        winning_party = max(votes_by_party, key=votes_by_party.get)
        winning_party_by_municipality[municipality] = winning_party

    df_map = pd.DataFrame(list(winning_party_by_municipality.items()), columns=['MUNICIPIO', 'WinningParty'])
    df_map['Year'] = selected_year

    fig = px.choropleth(
        df_map, 
        geojson=geojson, 
        locations='MUNICIPIO', 
        color='WinningParty',
        featureidkey="properties.NOMGEO",  
        projection="mercator",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title=f"Partido Ganador por Municipio en Quintana Roo, {selected_year}")
    
    return fig  # Return the figure for this specific year

def plot_election_pie_chart(selected_year, selected_municipality, df_re_all_years, main_parties):

    # mapping years to their indices in the list of dataframes
    year_to_index = {2009: 0, 2012: 1, 2015:2, 2018: 3, 2021: 4}

    selected_year_index = year_to_index.get(selected_year)

    if selected_year_index is None:
        print(f"No data available for the year {selected_year}.")
        return
    
    # extract the dataframe for the selected year
    df_selected_year = df_re_all_years[selected_year_index]

    # filtering the df for the selected municipality
    df_municipality = df_selected_year[df_selected_year['MUNICIPIO'] == selected_municipality]
    if df_municipality.empty:
        print(f'No data available for {selected_municipality}.')
        return
    
    # aggregating votes for each main party
    votes_by_party = {main_party: 0 for main_party in main_parties}
    for party in main_parties:
        if party in df_municipality.columns:
            votes_by_party[party] += df_municipality[party].sum()

    # create the pie chart
    df_votes = pd.DataFrame(list(votes_by_party.items()), columns = ['Party', 'Votes'])
    fig = px.pie(df_votes, values = 'Votes', names = 'Party', 
                 title = f'Distribución de votos en {selected_municipality}, en {selected_year}')
    
    # Update the traces to remove the text labels
    fig.update_traces(textinfo='none', hoverinfo='label+percent')

    return fig

def plot_aggregated_votes_by_main_party_px(df_list, main_parties, selected_municipality, election_years):
    """
    Plots an interactive line plot with filled areas to zero for each main party and its alliances,
    in a selected municipality across elections using Plotly Express. This approximates the non-stacked
    area plot behavior of the original function.
    """
    # Initialize dictionary to hold vote totals for main parties
    votes_by_main_party = {main_party: [0] * len(election_years) for main_party in main_parties}

    # Loop through each DataFrame and year
    for i, (df, year) in enumerate(zip(df_list, election_years)):
        # Filter the DataFrame for the selected municipality
        if selected_municipality in df['MUNICIPIO'].values:
            filtered_df = df[df['MUNICIPIO'] == selected_municipality]
            
            # Loop through each main party and its alliances
            for party in main_parties:
                # Aggregate votes for each party in the alliance, adding to the main party's total
                if party in filtered_df.columns:
                    votes_by_main_party[party][i] += filtered_df[party].sum()

    # Prepare the data for plotting
    data_for_plotting = []
    for main_party, votes in votes_by_main_party.items():
        for year, vote in zip(election_years, votes):
            data_for_plotting.append({'Election Year': year, 'Total Votes': vote, 'Party': main_party})
    df_plot = pd.DataFrame(data_for_plotting)

    # Create the plot
    fig = px.line(df_plot, x='Election Year', y='Total Votes', color='Party',
                  line_shape='linear', title=f'Votos Totales por Partido (incluidas alianzas) en {selected_municipality}')
    
    # Customize the layout
    fig.update_traces(mode='lines', line=dict(width=2.5), fill='tozeroy')
    fig.update_layout(xaxis_title='Año Electoral',
                      yaxis_title='Votos Totales',
                      legend_title='Partido',
                      font=dict(family="Arial, sans-serif", size=12, color="#333"),
                      hovermode='x unified',
                      legend = dict(
                          orientation = 'h',
                          yanchor = 'bottom',
                          y = -0.6, # adjuist to fit layout
                          xanchor = 'center',
                          x = 0.5
                      ))
    
    return fig



# function to get the municipalities per selected year
def get_municipalities_per_year(df_dict, selected_year):
    df_selected = df_dict.get(selected_year)
    if df_selected is None:
        print(f"No data available for the year {selected_year}.")
        return []

    # Retrieve and return a sorted list of unique municipalities
    return sorted(df_selected['MUNICIPIO'].unique())


static_choropleth_percentage_women = create_gender_proportion_choropleth(df_ln_sx_qroo, geojson_data)
static_choropleth_age = create_age_choropleth(df_ln_age_qroo, geojson_data)
static_choropleth_totals = create_total_choropleth(df_ln_sx_qroo, geojson_data)
static_bar_totals = create_total_bar_plot(df_ln_sx_qroo)


# apply the vote split function to all the dataframes:




# Create a Dash application
app = Dash(__name__)

# Assuming you're fine with adding Bootstrap to your project
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    html.H1("Estadísticas de Elecciones", className='mb-4'),  # mb-4 is margin-bottom for spacing
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in sorted(set(election_years))],
            value=sorted(set(election_years))[0],
            className='mb-2',  # margin bottom
        ), width=6),  # Taking half width
        dbc.Col(dcc.Dropdown(
            id='municipio-dropdown'
            # Options set dynamically based on selected year
        ), width=6)
    ]),
   
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series-plot'), width=6)
    ], justify = 'center'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='pie-chart'), width=6)
    ], justify = 'center'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='choropleth-winning'), width=6)
    ], justify='center'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='choropleth-women', figure = static_choropleth_percentage_women), width=4),
        dbc.Col(dcc.Graph(id='choropleth-age', figure = static_choropleth_age), width=4)        
    ], justify = 'center'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-total-voters', figure = static_bar_totals), width=6),
        dbc.Col(dcc.Graph(id='choropleth-total-voters', figure = static_choropleth_totals), width=4)
    ])
], fluid=True)

# Callback to update municipio dropdown based on year selection
@app.callback(
    Output('municipio-dropdown', 'options'),
    Output('municipio-dropdown', 'value'),
    [Input('year-dropdown', 'value')]
)
def set_municipio_options(selected_year):
    # Assuming a function that returns municipios for a given year
    municipalities = get_municipalities_per_year(df_dict, selected_year)
    options = [{'label': m, 'value': m} for m in municipalities]
    new_value = municipalities[0] if municipalities else None  # Default to first municipality or None
    return options, new_value

# Callback to update interactive visualizations
@app.callback(
    [Output('time-series-plot', 'figure'),
     Output('pie-chart', 'figure'),
     Output('choropleth-winning', 'figure')],
    [Input('year-dropdown', 'value'),
     Input('municipio-dropdown', 'value')]
)
def update_visualizations(selected_year, selected_municipality):
    time_series_chart = plot_aggregated_votes_by_main_party_px(df_re_all_years, main_parties, selected_municipality, election_years)
    pie_chart_per_municipality_per_year = plot_election_pie_chart(selected_year, selected_municipality, df_re_all_years, main_parties)
    choropleth_winning_party_per_year = create_winning_party_per_year_choropleth(selected_year, geojson_data, main_parties, df_dict)
    return time_series_chart, pie_chart_per_municipality_per_year, choropleth_winning_party_per_year



if __name__ == '__main__':
    app.run_server(debug=True)
