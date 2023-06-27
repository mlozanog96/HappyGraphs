import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
#hints for debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import pandas as pd
import matplotlib.pyplot as plt

st.title('Explore Indicators')

st.write("Group KMJ Do-Gooders proudly presents: Happy Graphs - Graphs which make us optimistic.")

df= pd.read_csv('app/world_bank_data.csv')
available_indicators = df['indicator_name'].drop_duplicates().reset_index(drop=True)
selected_indicator = st.selectbox("Select an indicator", available_indicators)

df_indicator= df[df['indicator_name']==selected_indicator]
available_countries = df_indicator['country'].drop_duplicates().reset_index(drop=True)
selected_countries = st.multiselect("Select countries", available_countries, default=['World','Germany','Mexico']) #ACTION: make worldwide as a default

min_year = int(df_indicator['date'].min())
max_year = int(df_indicator['date'].max())
selected_year_range = st.slider("Select a year range", min_value=min_year, max_value=max_year, value=(1990,max_year))
selected_start_year, selected_end_year = selected_year_range

if not selected_countries:
    selected_countries=['World']

# Filter the data for selected countries and time period
filtered_data = df_indicator[['date','country','value']]
filtered_data = filtered_data[(filtered_data['date'] >= selected_start_year) & (filtered_data['date'] <= selected_end_year) & (df['country'].isin(selected_countries))]

# Group the data by country
grouped_data = filtered_data.groupby('country')

# Create a line chart for each country
fig, ax = plt.subplots()
for country, data in grouped_data:
    plt.plot(data['date'], data['value'], label=country)

# Customize the chart
plt.xlabel('Year')
plt.ylabel('KPI value')
plt.title('Linear Chart per Country: ',selected_indicator)
plt.legend()

# Show the chart
st.pyplot(fig)

# Capture mouse events and display tooltips
tooltip_data = {}
for line in lines:
    tooltip_data[line] = {
        'country': line.get_label(),
        'x': list(line.get_xdata()),
        'y': list(line.get_ydata())
    }

result = streamlit_bokeh_events(fig, events="MouseMove")
if result:
    if 'x' in result:
        x = result['x']
        for line, data in tooltip_data.items():
            idx = min(range(len(data['x'])), key=lambda i: abs(data['x'][i] - x))
            tooltip = f"Country: {data['country']}\nDate: {data['x'][idx]}\nValue: {data['y'][idx]}"
            line.set_label(f"{data['country']} ({data['y'][idx]})")
            st.pyplot(fig)
            st.markdown(tooltip)

# Pivot the data to create a matrix
matrix = pd.pivot_table(filtered_data, values='value', index='country', columns='date')

# Display the matrix using Streamlit
st.write(matrix)