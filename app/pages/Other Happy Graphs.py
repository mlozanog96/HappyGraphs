import streamlit as st
import altair as alt
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import numpy as np
import openai
import os
import requests
import json
from github import Github

st.markdown('# Other happy graphs :)')

df= pd.read_csv('app/world_bank_data.csv')

st.markdown('## Correlation between two variables')
filter_col1, filter_col2, filter_col3 = st.columns(3)
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator_1 = filter_col1.selectbox("Select 1st indicator", available_indicators)
selected_indicator_2 = filter_col2.selectbox("Select 2nd indicator", available_indicators)
df_indicator= df[(df['indicator_name']==selected_indicator_1) | (df['indicator_name']==selected_indicator_2)]

available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = filter_col3.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

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
st.write(matrix_data)
# Create a correlation scatter plot using Altair
chart = alt.Chart(matrix_data).mark_circle(size=60).encode(
    color='country:N',
    tooltip=['country', 'x','y']
).properties(
    width=600,
    height=400
)

# Display the scatter plot in Streamlit
st.altair_chart(chart, use_container_width=True)

### Get additional information on indicator
#Load secret key

#keys = {}
#with open("C:/Users/joana/Documents/GitHub/2023SSBIPMHWR/BigData/HappyGraphs/API_Keys", "r") as file:
#    for line in file:
#        line = line.strip()
#        if line:
#            key, value = line.split(" = ")
#            keys[key] = value.strip("'")
#openai_api_key = keys["openai_secret"]



### Get a response why this indicator is going up or down
# Filter the DataFrame based on the selected year range and countries
df_selected = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]

# Get the first and last data points for each country
df_first = df_selected.groupby('country')['value'].first().reset_index()
df_last = df_selected.groupby('country')['value'].last().reset_index()

# Determine the trend for each country
trend = None
if len(df_first) > 0:
    df_merged = pd.merge(df_first, df_last, on='country', suffixes=('_first', '_last'))
    df_merged['trend'] = df_merged.apply(lambda row: 'increase' if row['value_last'] > row['value_first'] else 'decrease' if row['value_last'] < row['value_first'] else 'steady', axis=1)
    trend = df_merged[['country', 'trend']]

# Display the trend information for each country
if trend is not None:
    st.write("Trend:")
    for _, row in trend.iterrows():
        st.write(f"{row['country']}: {row['trend']}")

st.markdown('# Radar Graph')

st.markdown('# Other charts')

### Get reason why indicator changes 
## Put this answer in prompt to 
# COMMENT: Joana: I can do that. I have it prepared already, but want the trend to be working / need some thoughts on that