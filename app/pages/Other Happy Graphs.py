import streamlit as st
import altair as alt
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import numpy as np
import openai
import os
import requests
import json
import numpy
from github import Github
import seaborn as sns
import matplotlib.pyplot as plt

st.markdown('# Other happy graphs! :)')

df= pd.read_csv('app/world_bank_data.csv')

st.markdown('## Correlation between two variables')
filter_col1, filter_col2 = st.columns(2)
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator_1 = filter_col1.selectbox("Select 1st indicator", sorted(available_indicators),index=2)
selected_indicator_2 = filter_col2.selectbox("Select 2nd indicator", sorted(available_indicators),index=3)
df_indicator= df[(df['indicator_name']==selected_indicator_1) | (df['indicator_name']==selected_indicator_2)]

available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['Germany']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
selected_start_year, selected_end_year = selected_year_range

if not selected_countries:
    selected_countries = ['World']

# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]
filtered_data = filtered_data.sort_values('date')

def convert_table_to_matrix(table):
    # Pivot the table to create separate columns for each indicator
    matrix = table.pivot(index=['country', 'date'], columns='indicator_name', values='value').reset_index()
    
    return matrix

matrix_data= convert_table_to_matrix(filtered_data)

# Set Color palette
num_colors= 15
color_palette = sns.color_palette("husl", num_colors)
custom_palette = [sns.color_palette("hls", num_colors).as_hex()[i] for i in range(num_colors)]

# Create a correlation scatter plot using Altair
chart = alt.Chart(matrix_data).mark_circle(size=60).encode(
    x=alt.X(f"{selected_indicator_1}:Q"),
    y=alt.Y(f"{selected_indicator_2}:Q"),
    color=alt.Color('country',scale=alt.Scale(range=custom_palette)),
    tooltip=['date','country', f"{selected_indicator_1}", f"{selected_indicator_2}"]
).properties(
    width=600,
    height=400
)
correlation = np.corrcoef(matrix_data[selected_indicator_1], matrix_data[selected_indicator_2])[0, 1]


# Display the scatter plot in Streamlit
st.altair_chart(chart, use_container_width=True)

# Calculate correlation
correlation = np.corrcoef(matrix_data[selected_indicator_1], matrix_data[selected_indicator_2])[0, 1]
st.write(f"Correlation: {correlation:.2f}")

st.write(df)


st.markdown('## Radar Graph second try')
available_indicators_radar = df[df['indicator_name'].isin(['People using at least basic drinking water services',
                                                             'Open defecation',
                                                             'Vulnerable employment female',
                                                             'Vulnerable employment male',
                                                             'Vulnerable employment, total',
                                                             'Proportion of seats held by women in national parliaments',
                                                             'Access to electricity',
                                                             'Forest area',
                                                             'Renewable energy consumption % stagnates',
                                                             'Population density'])]['indicator_name'].drop_duplicates().tolist()

col1, col2 = st.columns(2)
default_indicators = ['People using at least basic drinking water services', 'Forest area', 'Access to electricity']
radar_indicators = col1.multiselect("Select indicators", sorted(available_indicators_radar), default=default_indicators)
df_indicator_radar = df[df['indicator_name'].isin(radar_indicators)]

available_countries_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
radar_countries = col1.multiselect("Select countries", sorted(available_countries_radar), default=['World','Germany','Mexico'])
df_indicator_radar= df_indicator_radar[df_indicator_radar['country'].isin(radar_countries)]

available_years_radar=df_indicator_radar['date'].drop_duplicates().reset_index(drop=True)
year=col2.selectbox("Select year",sorted(available_years_radar, reverse=True), index=1)
df_radar= df_indicator_radar[df_indicator_radar['date']==year]
df_radar=df_radar.drop('date',axis=1)

'''
Creation of radar graph function
'''
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
        value_single = []

        # Iterate over the filtered values and append them to the value_single list
        for row in x:
            value_single.append(row)

        # Append the first value at the end to close the radar plot
        value_single = np.concatenate((value_single, [value_single[0]]))

        # Scale the values between 1 and 5
        min_val = np.min(value_single)
        max_val = np.max(value_single)
        scaled_values = 1 + ((value_single - min_val) / (max_val - min_val)) * 4

        # Append the scaled values to the list of values for all countries
        values_allcountries.append(scaled_values)

    # Create the plot
    label_placement = np.linspace(start=0, stop=2*np.pi, num=len(scaled_values))
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)

    # Plot the radar lines for each country
    for array in values_allcountries:
        ax.plot(label_placement, array)

    # Set the category labels on the x-axis
    ax.set_xticks(np.linspace(0, 2*np.pi, len(categories), endpoint=False))
    ax.set_xticklabels(categories)

    # Add legend with country names
    ax.legend(country_list)

    return fig

# Display the radar plot
st.pyplot(create_radar(df_radar))




st.markdown('## Radar Graph before try')


st.markdown('## Radar Graph')
col1, col2 = st.columns(2)
radar_indicators= st.multiselect("Select indicators", sorted(available_indicators), default=['Life expectancy','Forest area','Access to electricity','Energy use','Refugee population'])
df_indicator_radar= df[df['indicator_name'].isin(radar_indicators)]

available_countries_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
radar_countries = col1.multiselect("Select countries", sorted(available_countries_radar), default=['World','Germany','Mexico'])
df_indicator_radar= df_indicator_radar[df_indicator_radar['country'].isin(radar_countries)]

available_years_radar=df_indicator_radar['date'].drop_duplicates().reset_index(drop=True)
year=col2.selectbox("Select year",sorted(available_years_radar, reverse=True), index=1)
df_radar= df_indicator_radar[df_indicator_radar['date']==year]
df_radar=df_radar.drop('date',axis=1)

st.write(df_radar)
# Get unique indicators
unique_indicators = df_radar['indicator_name'].unique()

# Create angles for each indicator
num_indicators = len(unique_indicators)
angles = np.linspace(0, 2 * np.pi, num_indicators, endpoint=False).tolist()

# Create the chart with Matplotlib
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
for country, data in df_radar.groupby('country'):
    values = [data[data['indicator_name'] == ind]['value'].values[0] if ind in data['indicator_name'].values else 0 for ind in unique_indicators]
    values += values[:1]  # Close the shape of the plot
    ax.plot(angles, values, label=country)
    ax.fill(angles, values, alpha=0.25)  # Fill the area under the plot

ax.set_xticks(angles)
ax.set_xticklabels(unique_indicators)
ax.set_yticks([])  # Hide radial axis labels
ax.set_title('Radar Graph')
ax.legend()

# Display the chart in Streamlit
st.pyplot(fig)


