import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import numpy as np

st.title('Other charts')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

df= pd.read_csv('app/world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator = st.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(1990,max_year))
selected_start_year, selected_end_year = selected_year_range


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
    trend = df_merged['trend'].tolist()

# Display the trend information
st.write("Trend:", trend)


### Get reason why indicator changes 
## Put this answer in prompt to 