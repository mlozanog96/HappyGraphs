# Import packages
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils import ai_assistant


st.markdown('# Other happy graphs! :)')

# Load dataset with all indicators
df= pd.read_csv('app/data/world_bank_data.csv')

st.markdown('## Heat Map: Correlation between variables')
## Heat map
# Create list of indicators based on the dataset
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
# Show box to select one or more indicators, indicators, including some default values
selected_indicators = st.multiselect("Select indicators to add in HeatMap", sorted(available_indicators), default=['Labor force female','GDP growth % mostly above 0 (but decreasing)','Inflation','Suicides','CO2 emissions','Agricultural methane emissions'])
# If we do not have any selected country, show some indicators 
if not selected_indicators:
    selected_indicators = ['CO2 emissions','Agricultural methane emissions']


# Create list of available countries based on the dataset
available_countries = df['country'].drop_duplicates().reset_index(drop=True)
# Show box to select one or more countries, including some default values
selected_countries = st.multiselect("Select countries", available_countries, default=['World']) 
# If we do not have any selected country, show World
if not selected_countries:
    selected_countries = ['World']

# Filter dataset based on countries and indicators
df_countries=  df[(df['country'].isin(selected_countries)) &((df['indicator_name'].isin(selected_indicators)))]

# Define min and max year in the selected dataset
min_year = int(df_countries['date'].min())
max_year = int(df_countries['date'].max())
# Show slider with available years, default value: 2000 to max
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
selected_start_year, selected_end_year = selected_year_range

# Filter the data for selected time period
df_years=  df_countries[(df_countries['date'] >= selected_start_year) & (df_countries['date'] <= selected_end_year)]

# Abbreviations of indicator names to show in the heatmap
abbreviation_mapping = {
    'Life expectancy': 'LE',
    'People using at least basic drinking water services': 'BWS',
    'Suicides': 'Suicides',
    'Open defecation': 'OD',
    'Sanitation service': 'SS',
    'Inflation': 'Inflation',
    'Vulnerable employment female': 'VE Female',
    'Vulnerable employment male': 'VE Male',
    'Vulnerable employment, total': 'VE Total',
    'GDP growth % mostly above 0 (but decreasing)': 'GDP Growth',
    'Labor force female': 'LF Female',
    'Labor force total': 'LF Total',
    'Military expenditure': 'Mil. Expenditure',
    'Proportion of seats held by women in national parliaments': 'Seats Held by Women',
    'Scientific technical journal articles': 'Sci. Journal Articles',
    'Mortality caused by road traffic': 'Road Traffic Mortality',
    'Access to electricity': 'Access to Electricity',
    'Access to clean fuels and technologies for cooking': 'Clean Cooking',
    'Refugee population': 'Refugee Population',
    'Forest area': 'Forest Area',
    'Agricultural methane emissions': 'Agri. Methane Emissions',
    'CO2 emissions': 'CO2 Emissions',
    'Energy use': 'Energy Use',
    'Renewable energy consumption % stagnates': 'Renew. Energy Consumption',
    'Total greenhouse gas emissions': 'GHG Emissions',
    'Population density': 'Pop. Density'
}
# Convert indicator name to abbreviation based on a list
df_years['indicator_name'] = df_years['indicator_name'].replace(abbreviation_mapping)


# Pivot the data to create a correlation matrix
correlation_matrix_data = df_years.pivot_table(index=['country', 'date'], columns='indicator_name', values='value')

# Calculate the correlation between indicators
correlation_matrix = correlation_matrix_data.corr()

# Create the heatmap using seaborn
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)

# Adjust the axis labels and the title of the plot
ax.set_xlabel('Indicators')
ax.set_ylabel('Indicators')
ax.set_title('Correlation Heatmap of Indicators')

# Display the heatmap
st.pyplot(fig)

## Correlation between two variables
st.markdown('## Correlation between two variables')
st.write('Indicators, Countries and Year range is determine for Heatmap filters')
# Create 2 columns to distribute dropdown lists for indicators
filter_col1, filter_col2 = st.columns(2)
# Create list of indicator names and show values (default values: 1st and 2nd variables in the list)
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator_1 = filter_col1.selectbox("Select 1st indicator", sorted(selected_indicators),index=0)
selected_indicator_2 = filter_col2.selectbox("Select 2nd indicator", sorted(selected_indicators),index=1)
# Filter dataset for two selected indicators
df_indicator= df[(df['indicator_name']==selected_indicator_1) | (df['indicator_name']==selected_indicator_2)]


# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]
filtered_data = filtered_data.sort_values('date')

# Create matrix to create scatter plot
matrix_filtered_data= filtered_data.pivot_table(index=['country', 'date'], columns='indicator_name', values='value').reset_index()

# Set Color palette
num_colors= 15
color_palette = sns.color_palette("husl", num_colors)
custom_palette = [sns.color_palette("hls", num_colors).as_hex()[i] for i in range(num_colors)]

# Create a correlation scatter plot using Altair
chart = alt.Chart(matrix_filtered_data).mark_circle(size=60).encode(
    x=alt.X(f"{selected_indicator_1}:Q"),
    y=alt.Y(f"{selected_indicator_2}:Q"),
    color=alt.Color('country',scale=alt.Scale(range=custom_palette)),
    tooltip=['date','country', f"{selected_indicator_1}", f"{selected_indicator_2}"]
).properties(
    width=600,
    height=400
)

# Display scatter plot
st.altair_chart(chart, use_container_width=True)

# Calculate correlation between two selected variables
correlation = matrix_filtered_data[selected_indicator_1].corr(matrix_filtered_data[selected_indicator_2])

# Display correlation value
st.write("Correlation:", correlation)


## Radar Graph
st.markdown('## Radar Graph')
st.write('The following Graph shows you a comparison of countries. As indicators you can choose all our indicators which are percentage scale. Happy exploring!')

# Select indicators that allow to have a clear comparisson (6 indicators removed)
available_indicators_radar = df[df['indicator_name'].isin(['Life expectancy',
                                                           'People using at least basic drinking water services',
                                                           'Suicides',
                                                           'Open defecation',
                                                           'Sanitation service',
                                                           'Inflation',
                                                           'Vulnerable employment female',
                                                           'Vulnerable employment male',
                                                           'Vulnerable employment, total',
                                                           'GDP growth % mostly above 0 (but decreasing)',
                                                           'Labor force female',
                                                           'Military expenditure',
                                                           'Proportion of seats held by women in national parliaments',
                                                           'Access to electricity',
                                                           'Access to clean fuels and technologies for cooking',
                                                           'Forest area',
                                                           'CO2 emissions',
                                                           'Energy use',
                                                           'Total greenhouse gas emissions',
                                                           'Population density'])]['indicator_name'].drop_duplicates().reset_index(drop=True)

# Create 2 columns to distribute dropdown lists for countries and selected year
col1, col2 = st.columns(2)
# Create a variable with default values (list)
default_indicators = ['Sanitation service', 'Vulnerable employment female', 'People using at least basic drinking water services', 'Forest area', 'Access to electricity']
# Box to include indicators to show in the radarchart
radar_indicators = st.multiselect("Select indicators", sorted(available_indicators_radar), default=default_indicators)
# If we do not have any selected indicator, show default indicators 
if not radar_indicators:
    radar_indicators= default_indicators
# Filter indicators in dataframe
df_indicator_radar = df[df['indicator_name'].isin(radar_indicators)]
# Convert indicator name to abbreviation based on a list
df_indicator_radar['indicator_name'] = df_indicator_radar['indicator_name'].replace(abbreviation_mapping)

# Create list of available countries for radar chart
available_countries_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
# Show box to select multiple countries, default values: World, Germany and Mexico
radar_countries = col1.multiselect("Select countries", sorted(available_countries_radar), default=['World','Germany','Mexico'])
# If we do not have any selected country, show World
if not radar_countries:
    radar_countries = ['World']
# Filter dataset using selected countries for radar chart
df_indicator_radar= df_indicator_radar[df_indicator_radar['country'].isin(radar_countries)]

# Create a list with available years in dataset pre-filtered
available_years_radar=df_indicator_radar['date'].drop_duplicates().reset_index(drop=True)
# Dropdown list to show available years
year=col2.selectbox("Select year",sorted(available_years_radar, reverse=True), index=1)
# Filter dataset based on selected year
df_radar= df_indicator_radar[df_indicator_radar['date']==year]
df_radar=df_radar.drop('date',axis=1)


# Creation of radar graph function
def create_radar(df_indicator_radar):
    # Get unique categories
    categories = df_indicator_radar['indicator_name'].unique()

    # Calculate the values for each country
    values_allcountries = []
    country_list = []

    # Iterate over unique countries
    for country in df_indicator_radar['country'].unique():
        country_list.append(country)

        # Filter data for the current country
        x = df_indicator_radar[df_indicator_radar['country'] == country]['value']
        value_single = np.zeros(len(categories))

        # Iterate over the filtered values and append them to the value_single list
        for i, row in enumerate(x):
             value_single[i] = row

        # Append the first value at the end to close the radar plot
        value_single = np.concatenate((value_single, [value_single[0]]))

        # Append the scaled values to the list of values for all countries
        values_allcountries.append(value_single)

    # Create the plot
    label_placement = np.linspace(start=0, stop=2*np.pi, num=len(value_single))
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)

    # Plot the radar lines for each country
    for array in values_allcountries:
        ax.plot(label_placement, array)

    # Set the category labels on the x-axis
    ax.set_xticks(np.linspace(0, 2*np.pi, len(categories), endpoint=False))
    ax.set_xticklabels(categories)

    # Add legend with country names
    ax.legend(country_list, loc='upper right')

    return fig

# Display the radar plot
st.pyplot(create_radar(df_radar))


# Having fun
st.markdown('# And lastly, here is a funny poem why Happy Graphs is awesome!')
st.write('Disclaimer: The following poem is generated using the model gpt 3.5 turbo by openai. For more information click here: https://platform.openai.com/docs/models/gpt-3-5')
prompt_poem = 'Write me a poem on why Graphs, that show bad world bank indicators which decrease and good world bank indicators which increase, make us happy and inspire us to do good in under 200 tokens.'
answer = ai_assistant(prompt_poem)
st.write(answer)
st.markdown('##### We hope we made your worldview more positive and inspired you to take action. Best, the Group KMJ Do-Gooders')