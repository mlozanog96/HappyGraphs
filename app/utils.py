import pandas as pd
import requests
#import openai
import json
#from statsmodels.tsa.stattools import adfuller
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Ridge

def get_data(id_indicator, countries):

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

        # create a dataframe out of that
        data = {'Country': countries, 'Date': dates, 'Value': values}
        df = pd.DataFrame(data)

        df_complete = pd.concat([df_complete, df], ignore_index=True)


    return(df_complete)


def ad_test(df):
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


    # loop over all countrys in the dataframe
    for country in df['Country'].unique():
        
        model = Ridge(alpha = alpha)

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
            

    
def get_indicator_reason(reason_indicator, df_year_max, df_year_min, reason_countries='worldwide'):
    keys ={}
    
    with open("../API_Keys", "r") as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split(" = ")
                keys[key] = value.strip("'")

    openai_api_key = keys["openai_secret"]
    openai.api_key = openai_api_key

    prompt_reason = 'summarize why has ' + reason_indicator + ' changed over the last ' + str(df_year_max - df_year_min) + ' in ' + reason_countries + ' so much, in under 400 tokens. Put the emphasis on the positive change in all countries.'
    response_reason = openai.Completion.create(engine="text-davinci-001", prompt=prompt_reason, max_tokens=400)
    answer = response_reason.choices[0].text.strip()
    return answer


def filter_projects(charity_country=None, charity_title=None, charity_region=None, charity_theme_name=None):
    keys ={}
    
    with open("../API_Keys", "r") as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split(" = ")
                keys[key] = value.strip("'")

    charity_key = keys["charity_secret"]

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

