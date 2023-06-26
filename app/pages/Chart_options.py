import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd

st.title('Happy Graphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

df= pd.read_csv('..\world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator = st.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(1990,max_year))
selected_start_year, selected_end_year = selected_year_range
