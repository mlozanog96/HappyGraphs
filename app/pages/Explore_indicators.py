# Import packages
import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from github import Github
import openai
from streamlit import components
import requests
from utils import ai_assistant, get_charity

st.title('Explore Indicators')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

openai_api_key = st.secrets["openai_secret"]
charity_api_key = st.secrets["charity_secret"]
openai.api_key=openai_api_key



# Create indicator and country filters
filter_col1, filter_col2 = st.columns(2)

df= pd.read_csv('app/data/world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
with filter_col1:
    selected_indicator = filter_col1.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
with filter_col2:
    selected_countries = filter_col2.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) 

# Create & Perform Prompt Explanation Indicator
button_pressed_indicator = False
if st.button("Press this button to get an explanation of this indicator"):
    button_pressed_indicator = True

if button_pressed_indicator == True:
    prompt_indicator = 'What is the indicator ' + selected_indicator + ' from the Worldbank Indicators database measuring? Name the unit of the indicator.'
    st.write('Disclaimer: The following indicator description is generated using the model gpt 3.5 turbo by openai. For more information click here: https://platform.openai.com/docs/models/gpt-3-5')
    answer = ai_assistant(prompt_indicator)
    st.write(answer)

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
SELECTED_START_YEAR, SELECTED_END_YEAR = selected_year_range

if not selected_countries:
    selected_countries = ['World']

# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= SELECTED_START_YEAR) & (df_indicator['date'] <= SELECTED_END_YEAR) & (df_indicator['country'].isin(selected_countries))]
filtered_data = filtered_data.sort_values('date')

# Set the axis values
x_scale = alt.Scale(domain=(SELECTED_START_YEAR, SELECTED_END_YEAR), nice=False)
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

# Get the first and last data points for each country
df_first = filtered_data.groupby('country')['value'].first().reset_index()
df_last = filtered_data.groupby('country')['value'].last().reset_index()

# Define icons for increase and decrease trends
increase_icon = "▲"
decrease_icon = "▼"

# Determine the trend for each country
trend = None
if len(df_first) > 0:
    df_merged = pd.merge(df_first, df_last, on='country', suffixes=('_first', '_last'))
    df_merged['Trend'] = df_merged['value_last'].sub(df_merged['value_first']).apply(lambda x: increase_icon if x > 0 else decrease_icon if x < 0 else '')
    trend = df_merged.pivot_table(index='country', values='Trend', aggfunc='first', fill_value='')

trends = {}
if trend is not None:
    trends = trend.to_dict()['Trend']

# Display the trend information for each country
if trend is not None:
    st.write("Trend")
    trend_matrix = pd.DataFrame.from_dict(trends, orient='index', columns=['Trend'])
    st.dataframe(trend_matrix)

# Pivot the data to create a matrix
matrix = pd.pivot_table(filtered_data, values='value', index='country', columns='date')


# Display the matrix using Streamlit
st.write("Data matrix")
st.dataframe(matrix)


st.markdown('### Why has this indicator changed as it has?')

# Create prompt to show the reason why the indicator has that trend using the prompt per country, as the dictionary of trend can't be made to a string in the prompt
prompt_prep_trend = None
for i, (country, trend) in enumerate(trends.items()):
    if i == 0:
        prompt_prep_trend = f"{trend} in {country}"
    else:
        prompt_prep_trend += f" and {trend} in {country}"


# Submit prompt to OpenAI
button_pressed = False
if st.button("Press this button to know why this indicator has changed as it has?"):
    button_pressed = True

if button_pressed == True:
    st.write('Disclaimer: The following explanation is generated using the model gpt 3.5 turbo by openai. For more information click here: https://platform.openai.com/docs/models/gpt-3-5')
    prompt_reason_trend = 'Explain why ' + selected_indicator + ' has ' + prompt_prep_trend + ' from ' + str(SELECTED_START_YEAR) + ' to ' + str(SELECTED_END_YEAR) + ' so much. Use under 400 tokens per country, if specific ones are indicated.'
    answer = ai_assistant(prompt_reason_trend)
    st.write(answer)



# Show matching charities
st.markdown('### What can you do to fuel a positive change?')
st.write('There are a lot of initiatives already out there working on positive change. See for yourself and let yourself be inspired to take action and support your favorite charity. We make a difference!')

# Load matching data
charity_map = pd.read_csv('app/data/charity_map.csv')
indicator_map = pd.read_csv('app/data/indicator_map.csv')


# Create indicator, charity theme and country filters
filter_col1, filter_col2, filter_col3 = st.columns(3)
# Indicator filter
all_indicators = [''] + list(indicator_map['indicator']) #[''] is for all indicators
with filter_col1:
    selected_indicators_charity = filter_col1.multiselect("Either select an indicator", all_indicators, placeholder="Choose an indicator") 
# Charity theme filter
all_charity_themes = [''] + list(charity_map['name']) #[''] is for all charities
with filter_col2:
    selected_charity_theme = filter_col2.multiselect("Or select a charity theme - caution: Don't select both an indicator and a charity theme", all_charity_themes, placeholder="Choose a charity theme")
# Country filter
all_countries = pd.read_csv('app/data/countries.csv') # english country names from: https://stefangabos.github.io/world_countries/
all_countries = [''] + list(all_countries['name']) #[''] is for all countries
with filter_col3:
    selected_countries_charity = filter_col3.multiselect("Select countries", all_countries, placeholder="Choose a country") 

# Indicator mapping to charity 
indicator_category = indicator_map[indicator_map['indicator'] == selected_indicator]
selected_category = indicator_category['category'].iloc[0]

# Filter the data based on the selected indicator & create list of charity themes
charity_category = charity_map[charity_map['category'] == selected_category]
charity_themes = charity_category['name'].tolist()
for selected_indicator_charity in selected_indicators_charity:
    st.write('The indicator ', selected_indicator_charity, ' is part of the category ', str(charity_category['category'].unique()), '. The charities in this category work in the following fields: ', charity_themes)


st.write('Below you find all the charities that work within your chosen theme and countries.')

if selected_indicators_charity and not selected_charity_theme:
    st.write('if')
    if len(selected_countries_charity) > 0:
        st.write('more than 0 countries')
        for selected_country in selected_countries_charity:
            for charity_theme in charity_themes:
                charities = get_charity(selected_countries_charity, selected_charity_theme, charity_theme, selected_country)
                st.write(charities)
    else:
        st.write('less than 0 countries')
        for charity_theme in charity_themes:
                charities = get_charity(selected_countries_charity, selected_charity_theme, charity_theme, selected_country = '')
                st.write(charities)
elif selected_charity_theme and not selected_indicators_charity:
    st.write('first elif')
    if len(selected_countries_charity) > 0:
        for selected_country in selected_countries_charity:
            for selected_theme in selected_charity_theme:
                charities = get_charity(selected_countries_charity, selected_charity_theme, selected_theme, selected_country)
                st.write(charities)
    else:
        st.write('less than 0 countries')
        for selected_theme in selected_charity_theme:
                charities = get_charity(selected_countries_charity, selected_charity_theme, selected_theme, selected_country = '')
                st.write(charities)
elif selected_indicators_charity and selected_charity_theme:
    st.write('second elif')
    st.write('You chose both an indicator and a charity theme. Please deselect one.')
else: 
    st.write('Waiting for your selection.')

# Inform the user about the source of the charity data and its limitations
st.write ('These charities are derived from the GlobalGiving API. For more information see: https://www.globalgiving.org/api/ . Please be aware that the API only allows to show 10 entries per request. To find more charities, please select other themes and/or countries.')