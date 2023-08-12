# Happy Graphs 
Welcome to our project "Happy Graphs"

# Motivation
The vision for this project was to create an application that let’s the users explore charts that make them optimistic. Inspired by the Gapminder (Gapminder, no date) project and books like Steven Pinker's “Enlightenment Now: The Case for Reason, Science, Humanism, and Progress” (Steven Pinker, 2023), we wanted to showcase that the status quo of the world is brighter than how many of us often perceive it. 

We believe that our daily view of the world is characterized by short-sightedness: We focus on what happens to us today, how the coffee machine was broken in the morning, and then news tell us what happened to others today and yesterday and what terrible things might await us tomorrow on election day. This perspective makes us focus on current bad events that make us empathize with others, but it also prevents us from acknowledging the long-term positive trends which humanity has achieved over the past decades. 

This is why we envisioned line graphs with trend analysis as the core elements of our application. As trends might come as a surprise to the users, we wanted to provide explanations on why this indicator developed like that per selected country. This way we hoped to not only spark interest but also start a data-based change of perspective underpinned with a coherent rationale. 

# Folder Structure
In our main folder, you can find:
* API_Keys: including the keys used for the APIs (OpenAI and Global Giving), we already configured these secret keys in Streamlit cloud
* Dockerfile: with the specifications for the container to deploy our website
* README.md: showing the structure of this GitHub
* app (folder): development of the complete application, explained with more detail in the following lines.

# app folder
Documents:
* Welcome_to_Happy_Graphs.py: Main page of our application, where you can predict and analyze life expectacy
* ultis.py: including the functions used frequently in our application
* requirements.txt: list of needed python libraries to deploy the application

Folders:
* archive: old python files with generated code in order to test functionalities that were included in the app
* data: csv files used in the app (data sources) and extra folder called preprocessing with python files needed to extract and preprocess the data (exploration, collection and cleaning)
* pages: python files with the pages of the deployment, Explore indicators and Other Happy Graphs 
* prediction_model: pkl file used in our application to predict life expectancy, python files including preprocessing of prediction model and another one with modeling approaches, and another folder with the data used for the life expectancy prediction (feed model and default values for Wrelcome to Happy Graphs page).

# Deployment
Resulting web page: https://happygraphs.streamlit.app/

# Contact
Please do not hesistate to contact us in case of any doubt:
- Kevin Giesen (s_giesen18@stud.hwr-berlin.de)
- Maria Lozano Gonzalez (s_lozanogonzalez22@stud.hwr-berlin.de)
- Joana Isabel Visel (s_visel22@stud.hwr-berlin.de) 