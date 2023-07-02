import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import numpy as np
import openai
import os
import requests
import json
from github import Github

st.title('Happy Grraphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")


st.markdown('## Other charts')

df= pd.read_csv('app/world_bank_data.csv')


### User selection
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator = st.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(1990,max_year))
selected_start_year, selected_end_year = selected_year_range

### Get additional information on indicator
# Load secret key

#keys = {}
#with open("C:/Users/joana/Documents/GitHub/2023SSBIPMHWR/BigData/HappyGraphs/API_Keys", "r") as file:
#    for line in file:
#        line = line.strip()
#        if line:
#            key, value = line.split(" = ")
#            keys[key] = value.strip("'")
#openai_api_key = keys["openai_secret"]

owner = 'mlozanog96'
repo = 'HappyGraphs'
secret_name = 'OPENAI_SECRET'

# Construct the URL to access the secret variable
url = f'https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}'

# Set the necessary headers for authentication
headers = {
    'Authorization': 'Bearer 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',
    'Accept': 'application/vnd.github.v3+json'
}

# Send a GET request to retrieve the secret variable
response = requests.get(url, headers=headers)
data = response.json()
st.write(data)

# Extract the value of the secret variable
#openai_api_key = data['value']

access_token = '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'
g = Github(access_token)
repo = g.get_repo('mlozanog96/HappyGraphs')  # Replace 'owner/repository' with the actual repository path
secret_name = 'OPENAI_SECRET'  # Replace with the actual secret key name
secret_value = repo.get_secret(secret_name).value
st.write(secret_value)





 # Create & Perform Prompt
prompt_indicator = 'What is the indicator ' + selected_indicator + ' from the Worldbank Indicators database measuring? Name the measure unit.'
response_indicator = openai.Completion.create(engine="text-davinci-001", prompt=prompt_indicator, max_tokens=400)
answer = response_indicator.choices[0].text.strip()
st.write(answer)

### Line chart



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

### Get reason why indicator changes 
## Put this answer in prompt to 
# COMMENT: Joana: I can do that. I have it prepared already, but want the trend to be working / need some thoughts on that