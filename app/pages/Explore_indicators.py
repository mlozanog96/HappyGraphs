import streamlit as st
import altair as alt
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from github import Github
import openai
from streamlit import components
import requests

st.title('Explore Indicators')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

#ACTION: remove commenting befor submitting
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


st.markdown('### Why has this indicator changed in the countries?')

# Show the reason why it has that trend
prompt_prep_trend = None
for i, (country, trend_per_country) in enumerate(trends.items()):
    if i == 0:
        prompt_prep_trend = f"{trend_per_country} in {country}"
    else:
        prompt_prep_trend += f" and {trend_per_country} in {country}"
#ACTION: remove commenting befor submitting
# prompt_reason_trend = 'Explain why ' + selected_indicator + ' has ' + prompt_prep_trend + ' from ' + str(SELECTED_START_YEAR) + ' to ' + str(SELECTED_END_YEAR) + ' so much. Use about 400 tokens per country.'
# response_reason_trend = openai.Completion.create(engine="text-davinci-001", prompt=prompt_reason_trend, max_tokens=400)
# answer = response_reason_trend.choices[0].text.strip()
# st.markdown(answer)


# Show matching charities
st.markdown('### What can you do to fuel a positive change?')
st.write('There are a lot of initiatives already out there working on your chosen indicator. See for yourself. Let youself be inspired to take action yourself and support your favorised charity. We make a diffrence!')

indicator_map = pd.read_csv('app/indicator_map.csv')
charity_map = pd.read_csv('app/charity_map.csv')

# Filter the data based on the selected indicator and find the corresponding category
st.write('Indicator Category')
indicator_category = indicator_map[indicator_map['indicator'] == selected_indicator]
selected_category = indicator_category['category'].iloc[0]

# Filter the data based on the selected indicator & create list of charity themes
charity_category = charity_map[charity_map['category'] == selected_category]
charity_theme = charity_category['name'].tolist()

st.write('The indicator ', selected_indicator, ' is part of the category ', selected_category, '. The charities in this category work in the following fields: ', charity_theme)
st.write('Below you find all the charities that work within these fields for your selected countries. Please note that there will be no matching charities if you have selected regions or the world in general.')


#ACTION put into utils
def formatting(data):
    if len(data) == 1:
        return f"'{data[0]}'"
    else:
        return [f"'{item}'" for item in data]
    
country_formatted = formatting(selected_countries)
theme_formatted = formatting(charity_theme)



url = "https://api.globalgiving.org/api/public/projectservice/all/projects/active?api_key="
response = requests.get(url + charity_api_key, headers={"Accept": "application/json"})

if response.status_code == 200:
    data = response.json()
    projects = data['projects']['project']

    for country in country_formatted:
        for theme in theme_formatted:
            filtered_projects = []

            for project in projects:
                pass_filters = True

                if project['country'] != country:
                    pass_filters = False
                    continue

                themes = project['themes']['theme']
                theme_names = [theme['name'] for theme in themes]
                if theme not in theme_names:
                    pass_filters = False
                    continue

                if pass_filters:
                    filtered_projects.append(project)

            if filtered_projects:
                for project in filtered_projects:
                    st.write("Project Title:", project['title'])
                    st.write("Countries:", project['country'])
                    themes = project['themes']['theme']
                    st.write("Themes:")
                    for theme in themes:
                        st.write("\tTheme ID:", theme['id'])
                        st.write("\tTheme Name:", theme['name'])
                    st.write("Summary:", project['summary'])
                    st.write("Funding:", project['funding'])
                    st.write("Goal:", project['goal'])
                    donation_options = project['donationOptions']['donationOption']
                    st.write("Donation Options:")
                    for donation in donation_options:
                        st.write("\tAmount:", donation['amount'], "$")
                        st.write("\tDescription:", donation['description'])
                    st.write("Project Link:", project['projectLink'])
                    st.write()
            else:
                st.write("No data found for", country, "and", theme)

else:
    st.write('Request failed with status code:', response.status_code)
