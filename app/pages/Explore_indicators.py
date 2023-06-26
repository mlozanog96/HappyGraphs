import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
#import plotly.express as px
#import pickle
import requests
#import openai
#import plotly.graph_objects as go


st.title('Happy Graphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

df= pd.read_csv('../app/world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator = st.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(1990,max_year))
selected_start_year, selected_end_year = selected_year_range


# Check if an indicator is selected
if not selected_indicator:
    st.text("Please choose an indicator to see its development.")
else:
    # Filter the data for selected countries and time period
    filtered_data = df_indicator[['date','country','value']]
    filtered_data = filtered_data[(filtered_data['date'] >= selected_start_year) & (filtered_data['date'] <= selected_end_year) & (df['country'].isin(selected_countries))]

    st.dataframe(filtered_data)