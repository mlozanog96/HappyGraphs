import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import requests
import openai
from utils import get_data, get_indicator_reason, filter_projects

st.title('Happy Graphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

intro_text = """
Increasing life expectancy is often regarded as a measure of societal progress. It reflects advancements in public health, education, technology, and social development. It indicates that societies are investing in improving the well-being of their citizens and addressing societal challenges.

Below you see a line graph showcasing how life expectancy has been increasing for many years worldwide. Increasing life expectancy makes us optimistic that the world is better off than we might sometimes think. Therefore, we invite you to explore more charts to make us happy.

Sidenote: Please don't get fooled by the decline of life expectancy since 2019. Research suggests that this is due to the Covid-19 pandemic, which has induced the first decline in global life expectancy since World War II. For further information, please read the [Nature Article](https://www.nature.com/articles/s41562-022-01450-3).
"""
st.markdown(intro_text, unsafe_allow_html=True)

df = pd.read_csv('world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator = st.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(1990,max_year))
selected_start_year, selected_end_year = selected_year_range