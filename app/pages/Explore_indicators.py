import streamlit as st
import altair as alt
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
    selected_countries = ['World']

# Filter the data for selected countries and time period
filtered_data = df_indicator[(df_indicator['date'] >= selected_start_year) & (df_indicator['date'] <= selected_end_year) & (df_indicator['country'].isin(selected_countries))]

# Group the data by country
grouped_data = filtered_data.groupby('country')

# Create a line chart for each country
fig, ax = plt.subplots()
tooltips = []

for country, data in grouped_data:
    line, = ax.plot(data['date'], data['value'], label=country)
    tooltip = ax.annotate("", xy=(0, 0), xytext=(-20, 20), textcoords="offset points",
                          bbox=dict(boxstyle="round", fc="white", edgecolor="gray"),
                          arrowprops=dict(arrowstyle="->"))
    tooltip.set_visible(False)
    tooltips.append(tooltip)

def update_tooltip(event):
    for i, data in enumerate(grouped_data):
        country = data[0]
        line = ax.lines[i]
        tooltip = tooltips[i]
        if line.contains(event)[0]:
            index = int(event.xdata)
            value = data[1].iloc[index]['value']
            x, y = line.get_data()
            x_val = x[index]
            y_val = y[index]
            tooltip.xy = (x_val, y_val)
            tooltip.set_text(f"{country}: {value}")
            tooltip.set_visible(True)
            fig.canvas.draw_idle()
        else:
            tooltip.set_visible(False)

fig.canvas.mpl_connect("motion_notify_event", update_tooltip)

# Customize the chart
ax.set_title(selected_indicator)
ax.set_xlabel('Year')
ax.set_ylabel(selected_indicator)
ax.set_xlim(selected_start_year, selected_end_year)
ax.legend()

# Show the chart
st.pyplot(fig)

# Pivot the data to create a matrix
matrix = pd.pivot_table(filtered_data, values='value', index='country', columns='date')

# Display the matrix using Streamlit
st.write(matrix)

# Set the axis values
x_scale = alt.Scale(domain=(selected_start_year, selected_end_year), nice=False)
y_scale = alt.Scale(domain=(filtered_data['value'].min(), filtered_data['value'].max()), nice=False)

# Create an Altair line chart with tooltips
chart = alt.Chart(data=filtered_data, mark='circle').mark_line().encode(
    x=alt.X('date:Q', scale=x_scale),
    y=alt.Y('value:Q', scale=y_scale),
    color='country',
    tooltip=['country', 'value']
)

# Show the chart using Streamlit
st.altair_chart(chart)