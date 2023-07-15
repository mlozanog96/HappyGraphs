
''' 
st.markdown('## Radar Graph')
col1, col2 = st.columns(2)
radar_indicators= st.multiselect("Select indicators", sorted(available_indicators), default=['Life expectancy','Forest area','Access to electricity','Energy use','Refugee population'])
df_indicator_radar= df[df['indicator_name'].isin(radar_indicators)]

available_countries_radar=df_indicator_radar['country'].drop_duplicates().reset_index(drop=True)
radar_countries = col1.multiselect("Select countries", sorted(available_countries_radar), default=['World','Germany','Mexico'])
df_indicator_radar= df_indicator_radar[df_indicator_radar['country'].isin(radar_countries)]

available_years_radar=df_indicator_radar['date'].drop_duplicates().reset_index(drop=True)
year=col2.selectbox("Select year",sorted(available_years_radar, reverse=True), index=1)
df_radar= df_indicator_radar[df_indicator_radar['date']==year]
df_radar=df_radar.drop('date',axis=1)

st.write(df_radar)
# Get unique indicators
unique_indicators = df_radar['indicator_name'].unique()

# Create angles for each indicator
num_indicators = len(unique_indicators)
angles = np.linspace(0, 2 * np.pi, num_indicators, endpoint=False).tolist()

# Create the chart with Matplotlib
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
for country, data in df_radar.groupby('country'):
    values = [data[data['indicator_name'] == ind]['value'].values[0] if ind in data['indicator_name'].values else 0 for ind in unique_indicators]
    values += values[:1]  # Close the shape of the plot
    ax.plot(angles, values, label=country)
    ax.fill(angles, values, alpha=0.25)  # Fill the area under the plot

ax.set_xticks(angles)
ax.set_xticklabels(unique_indicators)
ax.set_yticks([])  # Hide radial axis labels
ax.set_title('Radar Graph')
ax.legend()

# Display the chart in Streamlit
st.pyplot(fig)

'''