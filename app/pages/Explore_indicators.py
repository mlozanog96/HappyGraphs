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
from utils import ai_assistant

st.title('Explore Indicators')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

openai_api_key = st.secrets["openai_secret"]
charity_api_key = st.secrets["charity_secret"]
openai.api_key=openai_api_key



# Create a row layout for filters
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


# Create interactive filters for selecting charity theme and countries
filter_col1, filter_col2 = st.columns(2)
all_charity_themes = [''] + list(charity_map['name']) #[''] is for all charities
with filter_col1:
    selected_charity_theme = filter_col1.selectbox("Select a charity theme", all_charity_themes)
all_countries = pd.read_csv('app/data/countries.csv') # english country names from: https://stefangabos.github.io/world_countries/
all_countries = [''] + list(all_countries['name']) #[''] is for all countries
with filter_col2:
    selected_countries_charity = filter_col2.multiselect("Select countries", all_countries) 

st.write('Below you find all the charities that work within your chosen theme and countries.')

# Fetch charity data from the GlobalGiving API based on selected theme and countries
url = "https://api.globalgiving.org/api/public/projectservice/all/projects/active?api_key="
response = requests.get(url+charity_api_key, headers={"Accept": "application/json"})

if response.status_code == 200:
    data = response.json()
    projects = data['projects']['project']

    filtered_projects = []

    # Filter the projects based on selected countries and theme
    for project in projects:
        pass_filters = True

        if selected_countries_charity and project['country'] not in selected_countries_charity:
            pass_filters = False

        if selected_charity_theme and selected_charity_theme not in [theme['name'] for theme in project['themes']['theme']]:
            pass_filters = False

        if pass_filters:
            filtered_projects.append(project)

    # Display filtered charity projects and their details
    if filtered_projects:
        for project in filtered_projects:
            st.write("Project Title:", project['title'])
            st.write("Countries:", project['country'])
            themes = project['themes']['theme']
            for theme in themes:
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
        # Inform the user that no matching charities were found for the specified filters
        st.write('No data found for the specified filters. Please choose other countries or another theme.')

else:
    # Inform the user if the request to the GlobalGiving API failed and why
    st.write('Request failed with status code:', response.status_code)


# Inform the user about the source of the charity data and its limitations
st.write ('These charities are derived from the GlobalGiving API. For more information see: https://www.globalgiving.org/api/ . Please be aware that the API only allows to show 10 entries per request. To find more charities, please select other themes and/or countries.')


st.markdown('## Not so funny playground:')
indicator_map = pd.read_csv('app/data/indicator_map.csv')
# Filter the data based on the selected indicator and find the corresponding category
st.write('Indicator Category')
indicator_category = indicator_map[indicator_map['indicator'] == selected_indicator]
selected_category = indicator_category['category'].iloc[0]
st.write (indicator_category)

# Filter the data based on the selected indicator & create list of charity themes
charity_category = charity_map[charity_map['category'] == selected_category]
charity_theme = charity_category['name'].tolist()
st.write (charity_category)


st.write('The indicator ', selected_indicator, ' is part of the category ', selected_category, '. The charities in this category work in the following fields: ', charity_theme)
# st.write('Below you find all the charities that work within these fields for your selected countries. Please note that there will be no matching charities if you have selected regions or the world in general.')

all_indicators = [''] + list(indicator_map['indicator']) #[''] is for all indicators
with filter_col2:
    selected_indicator_charity = filter_col2.multiselect("Select indicator", all_indicators) 




#ACTION this only works for one country at the time
# url = "https://api.globalgiving.org/api/public/projectservice/all/projects/active?api_key="
# response = requests.get(url+charity_api_key, headers={"Accept": "application/json"})

# filters = {
#     'country': country_formatted,
#     'name': theme_formatted
# }

# if response.status_code == 200:
#     data = response.json()
#     projects = data['projects']['project']

#     filtered_projects = []

#     for project in projects:
#         pass_filters = True

#         for filter_column, filter_value in filters.items():
#             if filter_column == 'country' and filter_value and project['country'] not in filter_value:
#                 pass_filters = False
#                 break
#             if filter_column == 'name' and filter_value:
#                 themes = project['themes']['theme']
#                 theme_names = [theme['name'] for theme in themes]
#                 if filter_value not in theme_names:
#                     pass_filters = False
#                     break

#         if pass_filters:
#             filtered_projects.append(project)

#     if filtered_projects:
#         for project in filtered_projects:
#             st.write("Project Title:", project['title'])
#             st.write("Countries:", project['country'])
#             themes = project['themes']['theme']
#             st.write("Themes:")
#             for theme in themes:
#                 st.write("\tTheme ID:", theme['id'])
#                 st.write("\tTheme Name:", theme['name'])
#             st.write("Summary:", project['summary'])
#             st.write("Funding:", project['funding'])
#             st.write("Goal:", project['goal'])
#             donation_options = project['donationOptions']['donationOption']
#             st.write("Donation Options:")
#             for donation in donation_options:
#                 st.write("\tAmount:", donation['amount'], "$")
#                 st.write("\tDescription:", donation['description'])
#             st.write("Project Link:", project['projectLink'])
#             st.write()
#     else:
#         st.write('No data found for the specified filters: ', selected_countries, ',  ', selected_indicator, '. Please choose other countries or another indicator.')

# else:
#     st.write('Request failed with status code:', response.status_code)



#ACTION: This doesn't work yet
# url = "https://api.globalgiving.org/api/public/projectservice/all/projects/active?api_key="
# response = requests.get(url + charity_api_key, headers={"Accept": "application/json"})

# filters = {
#     'country': country_formatted,
#     'name': theme_formatted
# }

# if response.status_code == 200:
#     data = response.json()
#     projects = data['projects']['project']

#     for country in country_formatted:
#         for theme in theme_formatted:
#             filtered_projects = []

#             for project in projects:
#                 pass_filters = True

#                 if project['country'] != country:
#                     continue

#                 themes = project['themes']['theme']
#                 theme_names = [theme['name'] for theme in themes]
#                 if theme not in theme_names:
#                     continue

#                 filtered_projects.append(project)

#             if filtered_projects:
#                 for project in filtered_projects:
#                     st.write("Project Title:", project['title'])
#                     st.write("Countries:", project['country'])
#                     themes = project['themes']['theme']
#                     st.write("Themes:")
#                     for theme in themes:
#                         st.write("\tTheme ID:", theme['id'])
#                         st.write("\tTheme Name:", theme['name'])
#                     st.write("Summary:", project['summary'])
#                     st.write("Funding:", project['funding'])
#                     st.write("Goal:", project['goal'])
#                     donation_options = project['donationOptions']['donationOption']
#                     st.write("Donation Options:")
#                     for donation in donation_options:
#                         st.write("\tAmount:", donation['amount'], "$")
#                         st.write("\tDescription:", donation['description'])
#                     st.write("Project Link:", project['projectLink'])
#                     st.write()
#             else:
#                 st.write("No data found for", country, "and", theme)

# else:
#     st.write('Request failed with status code:', response.status_code)


#ACTION: trying
# url = "https://api.globalgiving.org/api/public/projectservice/all/projects/active?api_key="
# response = requests.get(url + charity_api_key, headers={"Accept": "application/json"})

# # filters = { #makes no diffrence whether in or out
# #     'country': country_formatted,
# #     'name': charity_theme
# # }

# if response.status_code == 200:
#     data = response.json()
#     projects = data['projects']['project']

#     for country in country_formatted:
#         for theme in theme_formatted:
#             filtered_projects = []

#             for project in projects:
#                 pass_filters = True

#                 if project['country'] != country:
#                     continue

#                 themes = project['themes']['theme']
#                 theme_names = [theme['name'] for theme in themes]
#                 if theme not in theme_names:
#                     continue

#                 filtered_projects.append(project)

#             if filtered_projects:
#                 for project in filtered_projects:
#                     st.write("Project Title:", project['title'])
#                     st.write("Countries:", project['country'])
#                     themes = project['themes']['theme']
#                     st.write("Themes:")
#                     for theme in themes:
#                         st.write("\tTheme ID:", theme['id'])
#                         st.write("\tTheme Name:", theme['name'])
#                     st.write("Summary:", project['summary'])
#                     st.write("Funding:", project['funding'])
#                     st.write("Goal:", project['goal'])
#                     donation_options = project['donationOptions']['donationOption']
#                     st.write("Donation Options:")
#                     for donation in donation_options:
#                         st.write("\tAmount:", donation['amount'], "$")
#                         st.write("\tDescription:", donation['description'])
#                     st.write("Project Link:", project['projectLink'])
#                     st.write()
#             else:
#                 st.write("No data found for", country, "and", theme)

# else:
#     st.write('Request failed with status code:', response.status_code)