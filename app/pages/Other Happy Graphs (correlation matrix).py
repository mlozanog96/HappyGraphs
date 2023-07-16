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
from utils import ai_assistant

st.markdown('# Other happy graphs! :)')

df= pd.read_csv('app/world_bank_data.csv')

st.markdown('## Correlation between two variables')
filter_col1, filter_col2 = st.columns(2)
available_countries = df['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['Germany']) #ACTION: make worldwide as a default

if not selected_countries:
    selected_countries = ['World']

df_countries=  df[df['country'].isin(selected_countries)]

min_year = int(df_countries['date'].min())
max_year = int(df_countries['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
selected_start_year, selected_end_year = selected_year_range

df_years=  df_countries[(df_countries['date'] >= selected_start_year) & (df_countries['date'] <= selected_end_year)]


# Pivot the data to have indicators as columns and rows representing pairs of indicators
pivoted_data = df_years.pivot(index='indicator_name', columns='indicator_name', values='value')

# Calculate the correlation matrix
correlation_matrix = pivoted_data.corr()

# Create the heatmap using seaborn
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)

# Adjust the axis labels and the title of the plot
ax.set_xlabel('Indicators')
ax.set_ylabel('Indicators')
ax.set_title('Correlation Heatmap of Indicators')

# Display the heatmap in Streamlit
st.pyplot(fig)

available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator_1 = filter_col1.selectbox("Select 1st indicator", sorted(available_indicators),index=2)
selected_indicator_2 = filter_col2.selectbox("Select 2nd indicator", sorted(available_indicators),index=3)
df_indicator= df[(df['indicator_name']==selected_indicator_1) | (df['indicator_name']==selected_indicator_2)]



# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]
filtered_data = filtered_data.sort_values('date')


def convert_table_to_matrix(table):
    # Pivot the table to create separate columns for each indicator
    matrix = table.pivot(index=['country', 'date'], columns='indicator_name', values='value').reset_index()
    return matrix

matrix_filtered_data= convert_table_to_matrix(filtered_data)

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
correlation = np.corrcoef(matrix_filtered_data[selected_indicator_1], matrix_filtered_data[selected_indicator_2])[0, 1]


# Display the scatter plot in Streamlit
st.altair_chart(chart, use_container_width=True)

# Calculate correlation
correlation = np.corrcoef(matrix_filtered_data[selected_indicator_1], matrix_filtered_data[selected_indicator_2])[0, 1]
st.write(f"Correlation: {correlation:.2f}")

st.markdown('## Radar Graph')
st.write('The following Graph shows you a comparison of countries. As indicators you can choose all our indicators which are percentage scale. Happy exploring!')


available_indicators_radar = df[df['indicator_name'].isin(['People using at least basic drinking water services',
                                                             'Open defecation',
                                                             'Sanitation service',
                                                             'Vulnerable employment female',
                                                             'Vulnerable employment male',
                                                             'Vulnerable employment, total',
                                                             'Proportion of seats held by women in national parliaments',
                                                             'Access to electricity',
                                                             'Forest area',
                                                             'Renewable energy consumption % stagnates'
                                                             ])]['indicator_name'].drop_duplicates().reset_index(drop=True)


col1, col2 = st.columns(2)
default_indicators = ['Sanitation service', 'Vulnerable employment female', 'People using at least basic drinking water services', 'Forest area', 'Access to electricity']
radar_indicators = st.multiselect("Select indicators", sorted(available_indicators_radar), default=default_indicators)
df_indicator_radar = df[df['indicator_name'].isin(radar_indicators)]

available_countries_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
radar_countries = col1.multiselect("Select countries", sorted(available_countries_radar), default=['World','Germany','Mexico'])
if not radar_countries:
    radar_countries = ['World']
df_indicator_radar= df_indicator_radar[df_indicator_radar['country'].isin(radar_countries)]

available_years_radar=df_indicator_radar['date'].drop_duplicates().reset_index(drop=True)
year=col2.selectbox("Select year",sorted(available_years_radar, reverse=True), index=1)
df_radar= df_indicator_radar[df_indicator_radar['date']==year]
df_radar=df_radar.drop('date',axis=1)

#Creation of radar graph function

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

# Map indicator



# Having fun
st.markdown('# And lastly here is a funny poem why Happy Graphs is awesome!')
st.write('Disclaimer: The following poems is generated using the model gpt 3.5 turbo by openai. For more information click here: https://platform.openai.com/docs/models/gpt-3-5')
prompt_poem = 'Write me a poem on why Graphs, that show bad world bank indicators which decrease and good world bank indicators which increase, in a positiv way make us happy and inspire us to make a positive impact on the world ourselves in under 200 tokens.'
answer = ai_assistant(prompt_poem)
st.write(answer)

st.markdown('### We hope we made your worldview more positive and inspired you to take action. Best, the Group KMJ Do-Gooders')