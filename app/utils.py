# Import packages
import pandas as pd
import requests
import openai
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Ridge
from statsmodels.tsa.stattools import adfuller



def get_data(id_indicator, countries):
    '''
    Function to fetch data for a specific indicator for multiple countries from the World Bank API
    Takes the 'id_indicator' as the indicator ID and 'countries' as a list of country names
    Returns a pandas DataFrame containing the retrieved data
    '''
    url = 'https://api.worldbank.org/v2/'

    #create empty Dataframe where the result is stored
    df_complete = pd.DataFrame()
    for country in countries:

        # create a new url
        requesting_url = url + f'country/{(country)}/indicator/{id_indicator}''?format=json'
        response = requests.get(requesting_url)

        # Parse the JSON response and extract the data
        if response.ok:
            data = response.json()

        else:
            print('Error: Request failed with status', response.status_code)

        # Accessing values, dates, and countries
        values = []
        dates = []
        countries = []

        # Extract values, dates, and countries from the JSON data
        for item in data[1]:
            values.append(item['value'])
            dates.append(int(item['date']))
            countries.append(item['country']['value'])

        # Create a dataframe out of that
        data = {'Country': countries, 'Date': dates, 'Value': values}
        df = pd.DataFrame(data)

        df_complete = pd.concat([df_complete, df], ignore_index=True)


    return(df_complete)


def ad_test(df):
    '''
    Function to perform the Augmented Dickey-Fuller test on a given time series 'df'
    Prints the ADF statistic, p-value, number of lags used, number of observations, and critical values
    '''
    dftest = adfuller(df, autolag='AIC')
    print('ADF: ', dftest[0])
    print('p-value: ', dftest[1])
    print('Number of Lags:', dftest[2])
    print('Number of Observations used:', dftest[3])
    print('critical Values:', dftest[4])
    for key, value in dftest[4].items():
        print("\t", key, ": ", value)


def evaluate_model(df, model):
    '''
    Function to evaluate model
    As an input the model and the dataframe is taken
    As result the function returns
    '''
    # array to store all test scores in order to average them out in the end
    all_scores = []
    all_mses = []
    countries_low_score = {}
    countries_high_score = {}
    countries_high_mse = {}
    models = {}


    # loop over all countrys in the dataframe
    for country in df['Country'].unique():
        
        country_data = df[df["Country"] == country]

        # data splitting 
        target = country_data['life_exp']
        features = country_data[country_data.columns.difference(['life_exp', 'Date'])]

        # split in train and test
        x_train, x_test, y_train, y_test = train_test_split(pd.get_dummies(features), target, test_size=0.3, random_state = 42)


        # Fitting the model on the training data
        model.fit(x_train, y_train)

        # Predicting on the testing data
        y_pred = model.predict(x_test)

        #Evaluating the model over test data 
        model_confidence = model.score(x_test, y_test)

        # calculate the mse 
        mse = mean_squared_error(y_test, y_pred)


        all_scores.append(model_confidence)     
        all_mses.append(mse)

        if model_confidence < 0.6:
            countries_low_score[country] = model_confidence
        
        else:
            countries_high_score[country] = model_confidence
            countries_high_mse[country] = mse
        
        
        models[country] = model

    
    return all_scores, all_mses, countries_low_score, countries_high_score, countries_high_mse, models
            


def create_ridge_model(df, alpha):
    '''
    Function to create a Ridge model for every country
    As an input the alpha of the model and the dataframe is taken
    As result the function returns models for all countries and calculated scores
    '''
    # array to store all test scores in order to average them out in the end
    all_scores = []
    all_mses = []
    countries_low_score = {}
    countries_high_score = {}
    countries_high_mse = {}
    models = {}


    # Loop over all countrys in the dataframe
    for country in df['Country'].unique():
        
        model = Ridge(alpha = alpha)

        country_data = df[df["Country"] == country]

        # Data splitting 
        target = country_data['life_exp']
        features = country_data[country_data.columns.difference(['life_exp', 'Date'])]

        # Split in train and test
        x_train, x_test, y_train, y_test = train_test_split(pd.get_dummies(features), target, test_size=0.3, random_state = 42)


        # Fitting the model on the training data
        model.fit(x_train, y_train)

        # Predicting on the testing data
        y_pred = model.predict(x_test)

        # Evaluating the model over test data 
        model_confidence = model.score(x_test, y_test)

        # Calculate the mse 
        mse = mean_squared_error(y_test, y_pred)


        all_scores.append(model_confidence)     
        all_mses.append(mse)

        if model_confidence < 0.6:
            countries_low_score[country] = model_confidence
        
        else:
            countries_high_score[country] = model_confidence
            countries_high_mse[country] = mse
        
        
        models[country] = model

    
    return all_scores, all_mses, countries_low_score, countries_high_score, countries_high_mse, models

def filter_projects(charity_country=None, charity_title=None, charity_region=None, charity_theme_name=None):
    '''
    Function to filter charity projects using the GlobalGiving API
    Accepts filters for country, title, region, and theme name to narrow down project search
    Returns a list of filtered projects based on the specified criteria
    '''
    # Collect GlobalGiving Key from Github and store in variable. 
    # charity_key = st.secrets["charity_secret"]

    url = "https://api.globalgiving.org/api/public/projectservice/all/projects/active?api_key="
    response = requests.get(url + charity_key, headers={"Accept": "application/json"})

    filters = {
        'country': charity_country,
        'title': charity_title,
        'region': charity_region,
        'name': charity_theme_name
    }

    if response.status_code == 200:
        data = response.json()
        projects = data['projects']['project']

        filtered_projects = []

        for project in projects:
            pass_filters = True

            for filter_column, filter_value in filters.items():
                if filter_column == 'country' and filter_value and project['country'] not in filter_value:
                    pass_filters = False
                    break
                if filter_column == 'title' and filter_value and project['title'] != filter_value:
                    pass_filters = False
                    break
                if filter_column == 'region' and filter_value and project['region'] != filter_value:
                    pass_filters = False
                    break
                if filter_column == 'name' and filter_value:
                    themes = project['themes']['theme']
                    theme_names = [theme['name'] for theme in themes]
                    if filter_value not in theme_names:
                        pass_filters = False
                        break

            if pass_filters:
                filtered_projects.append(project)

        if filtered_projects:
            return filtered_projects
        else:
            return None

    else:
        print('Request failed with status code:', response.status_code)
        return None


def get_country_data(country, data):
    '''
    Function to extract specific data related to a given country from the DataFrame 'data'
    Takes 'country' as the specific country's name and 'data' as a pandas DataFrame
    Returns a tuple containing various indicators for the specified country
    '''

    country_data = data[data['Country'] == country]
    access_to_electricity = country_data['access_to_electricity'].values[0]
    armed_forces = country_data['armed_forces'].values[0]
    child_immunization = country_data['child_immunization'].values[0]
    foreign_investm = country_data['foreign_investm'].values[0]
    gdp_per_cap = country_data['gdp_per_cap'].values[0]
    measels_immunitization = country_data['measels_immunitization'].values[0]
    net_primary_income = country_data['net_primary_income'].values[0]
    perc_overweigth = country_data['perc_overweigth'].values[0]
    primary_school_completion = country_data['primary_school_completion'].values[0]
    rural_population = country_data['rural_population'].values[0]
    trade_in_services = country_data['trade_in_services'].values[0]
    
    return (access_to_electricity, armed_forces, child_immunization, foreign_investm,
            gdp_per_cap, measels_immunitization, net_primary_income, perc_overweigth,
            primary_school_completion, rural_population, trade_in_services)


def ai_assistant(prompt, model = 'gpt-3.5-turbo', temperature = 0.5, max_tokens = 500):
    '''
    Function to generate a response using the OpenAI GPT-3.5 model as an AI assistant
    Takes 'prompt' as the starting text, 'model' as the GPT-3.5 model name, 'temperature' 
    controlling diversity and creativity of the output (= controlling the probability 
    distribution over the possible tokens at each step of the generation process), and 
    'max_tokens' to limit the response length. Returns the generated response based on 
    the provided prompt
    '''

    response = openai.ChatCompletion.create(
        model = model,
        messages = [{'role':'user','content': prompt}],
        temperature = temperature, 
        max_tokens = max_tokens,
    )

    # Retrieve the generated content from the OpenAI API response, stored in the 'choices' 
    # list at index 0, and access the content from the 'message' object's 'content' field. 
    content = response['choices'][0]['message']['content']

    return content

