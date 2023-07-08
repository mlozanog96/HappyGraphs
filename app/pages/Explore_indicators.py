import streamlit as st
import altair as alt
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from github import Github
import openai
from streamlit import components

st.title('Explore Indicators')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

openai_api_key = st.secrets["openai_secret"]
charity_api_key = st.secrets["charity_secret"]
openai.api_key=openai_api_key


# Create a row layout for filters
filter_col1, filter_col2 = st.columns(2)

df= pd.read_csv('app/world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
with filter_col1:
    selected_indicator = filter_col1.selectbox("Select an indicator", available_indicators)


df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
with filter_col2:
    selected_countries = filter_col2.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

# Create & Perform Prompt Explanation Indicator
prompt_indicator = 'What is the indicator ' + selected_indicator + ' from the Worldbank Indicators database measuring? Name the unit of the indicator.'
#ACTION: remove commenting befor submitting
#response_indicator = openai.Completion.create(engine="text-davinci-001", prompt=prompt_indicator, max_tokens=400)
#answer = response_indicator.choices[0].text.strip()
#st.write(answer)

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
# selected_start_year, selected_end_year = selected_year_range
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
    df_merged['Trend'] = df_merged.apply(lambda row: increase_icon if row['value_last'] > row['value_first'] else decrease_icon if row['value_last'] < row['value_first'] else '', axis=1)
    trend = df_merged[['country', 'Trend']]

trends = {}
if trend is not None:
    trends = {row['country']: row['Trend'] for _, row in trend.iterrows()}


# Display the trend information for each country in a matrix
if trend is not None:
    st.write("Trend")
    trend_matrix = trend.set_index('country').T
    st.dataframe(trend_matrix)
    
# Pivot the data to create a matrix
matrix = pd.pivot_table(filtered_data, values='value', index='country', columns='date')



# Display the matrix using Streamlit
st.write("Data matrix")
st.dataframe(matrix)


# Show the reason why it has that trend
for country, trend_per_country, selected_start_year, selected_end_year in trends.items():
    prompt_reason_trend = 'summarize why ' + selected_indicator + ' has ' + trend_per_country + ' from ' + str(selected_start_year) + ' to ' + str(selected_end_year) + ' in ' + country + ' so much, in under 400 tokens.'
    response_reason_trend = openai.Completion.create(engine="text-davinci-001", prompt=prompt_reason_trend, max_tokens=400)
    answer = response_reason_trend.choices[0].text.strip()
    # Perform further actions with the 'answer' variable
    st.write(answer)
# If the trend is ▲, put the emphasis on the positive change
# for country, trend_per_country in trends.items():
#     prompt_reason_trend = 'summarize why ' + selected_indicator + ' has ' + {trend_per_country} + ' in ' + {country} + ' from ' + str(SELECTED_START_YEAR) + ' to ' + str(SELECTED_END_YEAR) + ' so much, in under 400 tokens.'
#     response_reason_trend = openai.Completion.create(engine="text-davinci-001", prompt=prompt_reason_trend, max_tokens=400)
#     answer = response_reason_trend.choices[0].text.strip()
#     # Perform further actions with the 'answer' variable
#     st.write(answer)

'''
# this worked, but only took year in first prompt:
for country, trend_per_country, selected_start_year, selected_end_year in trends.items():
    prompt_reason_trend = 'summarize why ' + selected_indicator + ' has ' + trend_per_country + ' from ' + str(selected_start_year) + ' to ' + str(selected_end_year) + ' in ' + country + ' so much, in under 400 tokens.'
    response_reason_trend = openai.Completion.create(engine="text-davinci-001", prompt=prompt_reason_trend, max_tokens=400)
    answer = response_reason_trend.choices[0].text.strip()
    # Perform further actions with the 'answer' variable
    st.write(answer)
'''


# Show matching charities
