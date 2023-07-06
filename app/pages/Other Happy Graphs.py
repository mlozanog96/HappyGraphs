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

st.markdown('## Radar Graph')
col1, col2 = st.columns(2)
radar_indicators= st.multiselect("Select indicators", sorted(available_indicators), default=['Life expectancy','Forest area','Access to electricity','Energy use','Refugee population'])
df_indicator_radar= df[df['indicator_name'].isin(radar_indicators)]

available_countries_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
radar_countries = col1.multiselect("Select countries", sorted(available_countries_radar), default=['World','Germany','Mexico'])
df_indicator_radar= df[df['country'].isin(radar_countries)]

available_years_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
year=col2.selectbox("Select year",sorted(available_years_radar, reverse=True), index=0)


st.markdown('## Other charts')

### Get reason why indicator changes 
## Put this answer in prompt to 
# COMMENT: Joana: I can do that. I have it prepared already, but want the trend to be working / need some thoughts on that