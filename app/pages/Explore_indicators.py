import streamlit as st
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

if not selected_indicator:
    st.text("Please choose an indicator to see its development.")
else:
    # Filter the data for selected countries and time period
    filtered_data = df_indicator[['date','country','value']]
    filtered_data = filtered_data[(filtered_data['date'] >= selected_start_year) & (filtered_data['date'] <= selected_end_year) & (df['country'].isin(selected_countries))]

    st.dataframe(filtered_data)

     fig, ax = plt.subplots()
    ax.set_title(selected_indicator)
    ax.set_xlabel('Year')
    ax.set_ylabel(selected_indicator)
    ax.set_ylim(df[selected_indicator].min() - 10, df[selected_indicator].max() + 10)

    # Plot the data for selected countries
    for country in selected_countries:
        country_data = filtered_data[['Year', country]]
        line_color = st.color_picker(f"Select color for {country}", key=country)
        ax.plot(country_data['Year'], country_data[country], label=country, color=line_color)

        # Add a tooltip to show country and indicator value on hover
        tooltip = ax.annotate("", xy=(0, 0), xytext=(-20, 20), textcoords="offset points",
                              bbox=dict(boxstyle="round", fc="white", edgecolor="gray"),
                              arrowprops=dict(arrowstyle="->"))
        tooltip.set_visible(False)

        def update_tooltip(event):
            if event.inaxes == ax:
                x = int(event.xdata)
                y = int(event.ydata)
                tooltip.xy = (x, y)
                tooltip.set_text(f"{country}: {y}")
                tooltip.set_visible(True)
                fig.canvas.draw_idle()
            else:
                tooltip.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", update_tooltip)
    # Adjust x-axis scale based on the selected time period
    ax.set_xlim(selected_start_year, selected_end_year)
    # Add a legend
    ax.legend()

for country in df['country'].unique():
    data = df_grouped.loc[country]
    plt.plot(data.index, data.values, label=country)

plt.xlabel('Year')
plt.ylabel('KPI')
plt.title('Linear Chart of KPI per Country')
plt.legend()
plt.show()