import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import altair as alt
from pathlib import Path
import requests
import openai
import seaborn as sns
from utils import get_data, get_indicator_reason, filter_projects, get_country_data

st.title('Happy Graphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

st.markdown("# Playground")

# Load data
df_life_ex = pd.read_csv(Path(__file__).parent/'prediction_model/data/default-data.csv')
df= pd.read_csv('app/world_bank_data.csv')

### Life Expectancy
def load_model():
    with open(Path(__file__).parent/'pred_lifeexp.pkl', 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

loaded_model =load_model()

intro_text = """
Increasing life expectancy is often regarded as a measure of societal progress. It reflects advancements in public health, education, technology, and social development. It indicates that societies are investing in improving the well-being of their citizens and addressing societal challenges.

Below you see a line graph showcasing how life expectancy has been increasing for many years worldwide. Increasing life expectancy makes us optimistic that the world is better off than we might sometimes think. Therefore, we invite you to explore more charts to make us happy.

Sidenote: Please don't get fooled by the decline of life expectancy since 2019. Research suggests that this is due to the Covid-19 pandemic, which has induced the first decline in global life expectancy since World War II. For further information, please read the [Nature Article](https://www.nature.com/articles/s41562-022-01450-3).
"""
st.markdown(intro_text, unsafe_allow_html=True)

### Show life expectancy world wide compared to German & Mexican
# User selection
#ACTION: Search for an indicator by topic?

# Get the list of available indicators and countries and user selection
df_indicator= df[df['indicator_name']=='Life expectancy']
st.title('Life Expectancy')
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)

selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
selected_start_year, selected_end_year = selected_year_range

if not selected_countries:
    selected_countries = ['World']

# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]

# Set the axis values
x_scale = alt.Scale(domain=(selected_start_year, selected_end_year), nice=False)
y_scale = alt.Scale(domain=(filtered_data['value'].min(), filtered_data['value'].max()), nice=False)

# Set Color palette
num_colors= 15
color_palette = sns.color_palette("husl", num_colors)
custom_palette = [sns.color_palette("hls", num_colors).as_hex()[i] for i in range(num_colors)]

# Create an Altair line chart with tooltips
chart = alt.Chart(filtered_data).mark_line().encode(
    x=alt.X('date:Q', scale=x_scale),
    y=alt.Y('value:Q', scale=y_scale),
    color=alt.Color('country',scale=alt.Scale(range=custom_palette)),
    tooltip=['country', 'value']
).properties(
    width=800,
    height=400
    )+ alt.Chart(filtered_data).mark_circle().encode(
        x=alt.X('date:Q', scale=x_scale),
        y=alt.Y('value:Q', scale=y_scale),
        size=alt.value(20),
        color='country',
        tooltip=['country', 'value']
        )

# Show the chart using Streamlit
st.altair_chart(chart)

# Pivot the data to create a matrix
matrix = pd.pivot_table(filtered_data, values='value', index='country', columns='date')

# Display the matrix using Streamlit
st.write(matrix)

### Prediction with given features
st.markdown("## Prediction")
# User selection country
selected_country = st.selectbox("Select countries", sorted(available_countries), index=0) 
#selected_country = st.selectbox("Select country for default values", countries, default='World')
df_default= df[df['Country']==selected_country]

# Select default year
available_years = df_default['date'].drop_duplicates().reset_index(drop=True)
selected_year = st.selectbox("Select year for default values", sorted(available_years, reverse=True), index=0)

df_default= df_default[df_default['Date']==selected_year]

# Get data for the selected country
access_to_electricity, armed_forces, child_immunization, foreign_investm, gdp_per_cap, measels_immunitization, net_primary_income, perc_overweigth, primary_school_completion, rural_population, trade_in_services = get_country_data(selected_country, df_life_ex)

# Show default values / inputs
access_to_electricity = st.text_input('Access to electricity:', access_to_electricity)
st.write('Input:', access_to_electricity)



data = {
    'access_to_electricity': access_to_electricity,
    'armed_forces' : armed_forces, 
    'child_immunization' : child_immunization, 
    'foreign_investm' : foreign_investm, 
    'gdp_per_cap' : gdp_per_cap,
    'measels_immunitization' : measels_immunitization,
    'net_primary_income' : net_primary_income, 
    'perc_overweigth' : perc_overweigth,
    'primary_school_completion' : primary_school_completion,
    'rural_population' : rural_population, 
    'trade_in_services'	: trade_in_services,
}
# transform them into a Dataframe
#life_expect_df_test = pd.DataFrame(data, index=range(1))
# Predict using the loaded model
#life_expect_df_pred = loaded_model.predict(life_expect_df_test)

# Show predicted Life Expectancy
#st.write("Your predicted life expectancy is ", life_expect_df_pred[0], "years.")

# Display the extracted data used per country for the prediction
#st.write("Click on the 'Get Data' Button to inspect which data is used for the prediction")
#if st.button("Get Data"):
#    st.write(f"You selected the country: {selected_country}")
#    st.write("The following data was used for the prediction:")
#    st.write(f"Access to electricity: {access_to_electricity}")
#    st.write(f"Armed forces: {armed_forces}")
#    st.write(f"Child immunization: {child_immunization}")
#    st.write(f"Foreign investment: {foreign_investm}")
#    st.write(f"GDP per capita: {gdp_per_cap}")
#    st.write(f"Measles immunization: {measels_immunitization}")
#    st.write(f"Net primary income: {net_primary_income}")
#    st.write(f"Percentage overweight: {perc_overweigth}")
#    st.write(f"Primary school completion: {primary_school_completion}")
#    st.write(f"Rural population: {rural_population}")
#    st.write(f"Trade in services: {trade_in_services}")

#st.markdown("# Back to serious")




### Prediction with own features
#st.write("Now it's your turn!  Below you can predict the life expectancy for a fictive country that has the features you select. Feel free to play around and find out what has which impact on life expectancy:") 
#ACTION: make to input
#access_to_electricity = 100
#armed_forces = 3.338855e+06
#child_immunization = 100 
#foreign_investm = 1
#gdp_per_cap = 12000
#measels_immunitization = 97
#net_primary_income = 0 
#perc_overweigth = 10
#primary_school_completion = 100
#rural_population = 50
#trade_in_services = 15

#data = {
#    'access_to_electricity': access_to_electricity,
#    'armed_forces' : armed_forces, 
#    'child_immunization' : child_immunization, 
#    'foreign_investm' : foreign_investm, 
#    'gdp_per_cap' : gdp_per_cap,
#    'measels_immunitization' : measels_immunitization,
#    'net_primary_income' : net_primary_income, 
#    'perc_overweigth' : perc_overweigth,
#    'primary_school_completion' : primary_school_completion,
#    'rural_population' : rural_population, 
#    'trade_in_services'	: trade_in_services,
#}

# transform them into a Dataframe
#life_expect_df_test = pd.DataFrame(data, index=range(1))
# Predict using the loaded model
#life_expect_df_pred = loaded_model.predict(life_expect_df_test)
# Set up the Streamlit app
#st.write("In your fictive country a person has a predicted life expectancy of ", life_expect_df_pred[0], "years.")
