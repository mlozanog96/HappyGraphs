import streamlit as st
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import altair as alt
from pathlib import Path
import seaborn as sns
from utils import get_data, filter_projects, get_country_data #,get_indicator_reason

st.title('Happy Graphs')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

# Load data (default values / indicator values)
df_life_ex = pd.read_csv(Path(__file__).parent/'prediction_model/data/default-data.csv')
df= pd.read_csv('app/data/world_bank_data.csv')

### Life Expectancy
# Function to load life expectancy prediction model
def load_model():
    with open(Path(__file__).parent/'prediction_model/pred_lifeexp.pkl', 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

# Assign loaded model to a variable using the function
loaded_model =load_model()

intro_text = """
Increasing life expectancy is often regarded as a measure of societal progress. It reflects advancements in public health, education, technology, and social development. It indicates that societies are investing in improving the well-being of their citizens and addressing societal challenges.

Below you see a line graph showcasing how life expectancy has been increasing for many years worldwide. Increasing life expectancy makes us optimistic that the world is better off than we might sometimes think. Therefore, we invite you to explore more charts to make us happy.

Sidenote: Please don't get fooled by the decline of life expectancy since 2019. Research suggests that this is due to the Covid-19 pandemic, which has induced the first decline in global life expectancy since World War II. For further information, please read the [Nature Article](https://www.nature.com/articles/s41562-022-01450-3).
"""
st.markdown(intro_text, unsafe_allow_html=True)



### Show life expectancy world wide compared to German & Mexican

# Get the list of available countries for the user selection
# Filter indicator (only Life expectancy data)
df_indicator= df[df['indicator_name']=='Life expectancy']
st.title('Life Expectancy')
# Create variable with unique countries with Life Expectancy dataset 
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)

# Show box to select multiple countries, default values: World, Germany and Mexico
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) 

# If we do not have any selected country, show World
if not selected_countries:
    selected_countries = ['World']

# Define min and max year in the selected dataset
min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
# Show slider with available years, default value: 2000 to max
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(2000,max_year))
selected_start_year, selected_end_year = selected_year_range

# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]

# Set the axis values
x_scale = alt.Scale(domain=(selected_start_year, selected_end_year), nice=False)
y_scale = alt.Scale(domain=(filtered_data['value'].min(), filtered_data['value'].max()), nice=False)

# Set Color palette
num_colors= 15
color_palette = sns.color_palette("husl", num_colors)
custom_palette = [sns.color_palette("hls", num_colors).as_hex()[i] for i in range(num_colors)]

# Create a line chart
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

# Show chart
st.altair_chart(chart)

# Pivot the data to create a matrix
matrix = pd.pivot_table(filtered_data, values='value', index='country', columns='date')

# Display the matrix
st.write(matrix)

### Prediction with imaginative and given features
st.markdown("## Prediction")
intro_text_2 = """
To predict a value, you can select a country in order to get default values, then feel free to modify any value you want. \n 
The highest impact on your prediction will give the GDP per capita followed by the acces to electricity and primary school completion. 
Other Factors with a medium impact on the GDP of a country are the percentage of people with overweigth, the measels immutization, the rural population and foreign investments. 
Rather low impact on the predictions has the child immunitization, armed forces , trade in services and the primary net income. 
"""

st.markdown(intro_text_2, unsafe_allow_html=True)
## User selection country
# Select uniques values in default value dataframe
countries=df_life_ex['Country'].drop_duplicates().reset_index(drop=True)
# Dropdown list with sorted countries and default value World (261)
selected_country = st.selectbox("Select default country", sorted(countries), index=261) 
# Filter default values to predict life expectancy value
df_default= df_life_ex[df_life_ex['Country']==selected_country]

# Fuction to get data for the selected country/year
def get_value(indicator_name):
    df_default_value=df_default.loc[df_default['indicator_name'] == indicator_name, 'value']
    value= df_default_value.item() if len(df_default_value) > 0 else ""
    return value

# Get default values for all indicators
access_to_electricity_dv, armed_forces_dv, child_immunization_dv, foreign_investm_dv, gdp_per_cap_dv, measels_immunitization_dv, net_primary_income_dv, perc_overweigth_dv, primary_school_completion_dv, rural_population_dv, trade_in_services_dv = get_country_data(selected_country,df_life_ex)

# Create columns to distribute text inputs with all the indicators needed to predict life expectancy
col1, col2, col3, col4 = st.columns(4)

# Show text inputs including default values 
access_to_electricity = col1.text_input('Access to electricity:', access_to_electricity_dv)
armed_forces= col2.text_input('Armed Forces:', armed_forces_dv)
child_immunization = col3.text_input('Child immunization', child_immunization_dv)
foreign_investm= col4.text_input('Foreign Investment:', foreign_investm_dv)
gdp_per_cap= col1.text_input('GDP per capita:', gdp_per_cap_dv)
measels_immunitization= col2.text_input('Measels immunization:', measels_immunitization_dv)
net_primary_income= col3.text_input('Net primary income:', net_primary_income_dv)
perc_overweigth= col4.text_input('Overweigth Percentage:', perc_overweigth_dv)
primary_school_completion= col1.text_input('Primary school completion:', primary_school_completion_dv)
rural_population= col2.text_input('Rural population:', rural_population_dv)
trade_in_services =col3.text_input('Trade in services:', trade_in_services_dv)

# Create list with variables to predict life expectancy 
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

# Transform them into a Dataframe
life_expect_df_test = pd.DataFrame(data, index=range(1))

# Predict using the loaded model
life_expect_df_pred = loaded_model.predict(life_expect_df_test)

# Show predicted Life Expectancy
st.write("Your predicted life expectancy is ", life_expect_df_pred[0], "years.")