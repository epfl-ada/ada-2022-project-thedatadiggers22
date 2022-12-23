import pandas as pd
import numpy as np
import requests
import urllib
import ssl
import datetime
from iso3166 import countries
import plotly.express as px
import matplotlib as plt

COUNTRY_OWN_LANG = {"Italy" : "it", "Russia": "ru", "China": "zh", "Albania": "sq", 
"Bangladesh": "bn", "Botswana": "tn", "Cambodia": "km", "Croatia": "hr", "Greece": "el", "Sweden": "sv", "Finland": "fi", "Norway": "no",
 "Malaysia": "ms", "Israel": "he", "Lithuania": "lt", "Serbia": "sr", "Slovakia": "sk", "Slovenia": "sl", "Turkey": "tr",
 "Vietnam": "vi", "Bulgaria": "bg", "Czechia": "cs", "Denmark": "da", "Georgia": "ka", "Germany": "de", 
 "Hungary": "hu", "Iceland": "is", "Japan": "ja", "Kazakhstan": "kk", "South Korea": "ko", "Kyrgyzstan": 'ky', "Netherlands": "nl", "Poland": "pl", 
 "Romania": "ro", "Tajikistan": "tg", "Thailand": "th", "Azerbaijan": "az", "Mongolia": "mn"}

COUNTRY_OWN_LANG_TRUST_GOV = {"Italy" : "it", "Russia": "ru", "Albania": "sq", 
"Bangladesh": "bn", "Cambodia": "km", "Croatia": "hr", "Greece": "el", "Sweden": "sv", "Finland": "fi", "Norway": "no",
 "Malaysia": "ms", "Israel": "he", "Lithuania": "lt", "Serbia": "sr", "Slovakia": "sk", "Slovenia": "sl", "Turkey": "tr", "Bulgaria": "bg", "Czechia": "cs", "Denmark": "da", "Georgia": "ka", "Germany": "de", 
 "Hungary": "hu", "Japan": "ja", "Kazakhstan": "kk", "South Korea": "ko", "Kyrgyzstan": 'ky', "Netherlands": "nl", "Poland": "pl", 
 "Romania": "ro", "Thailand": "th", "Mongolia": "mn"}
 
COUNTRY_OWN_LANG_TRUST_GOV_MOBILITY= {"Italy" : "it", "Russia": "ru", 
"Bangladesh": "bn", "Croatia": "hr", "Greece": "el", "Sweden": "sv", "Finland": "fi", "Norway": "no",
 "Malaysia": "ms", "Israel": "he", "Lithuania": "lt", "Serbia": "sr", "Slovakia": "sk", "Slovenia": "sl", "Turkey": "tr", "Bulgaria": "bg", "Czechia": "cs", "Denmark": "da", "Georgia": "ka", "Germany": "de", 
 "Hungary": "hu", "Japan": "ja", "Kazakhstan": "kk", "South Korea": "ko", "Kyrgyzstan": 'ky', "Netherlands": "nl", "Poland": "pl", 
 "Romania": "ro", "Thailand": "th", "Mongolia": "mn"}
 
def get_country_dict(dict):
    '''
    Function to get the dict of countries of interest for specific dataset
    Inputs : 
        - dict : dataset  needed (original -> COVID-19; other trust dataset)
    Output : corresponding dict
    '''
    if dict == 'original' :
        return COUNTRY_OWN_LANG
    elif dict == 'trust gov' :
        return COUNTRY_OWN_LANG_TRUST_GOV
    elif dict == 'trust gov mobility':
        return COUNTRY_OWN_LANG_TRUST_GOV_MOBILITY


def json_to_df(json_obj, return_df):
    '''
    Function to be used within data fetching script

    Inputs : 

        - json_obj : dict that was fetched in the given iteration of the script
        - return_df : final df that will be return at the end of the script

    Output : concatenated df
    '''
    #Create df from json with nested list
    df = pd.DataFrame()
    if json_obj.get('title') == "Not found.":
        #print("Article not anymore in WikiData logs.")
        return pd.concat([return_df, df])
    try:
        df = pd.json_normalize(json_obj, record_path = ['items']).set_index(['timestamp']).drop(labels = ['project', 'granularity'
        , 'access', 'agent', 'article'], axis = 1)
    except:
        print("Error json to df")
        print(json_obj)
    #concatenation
    return  pd.concat([return_df, df])


def get_redirect_articles(title, lang, df_articles):
    '''
    Function to get the depreciated articles

    Inputs : 

        - title: title of the article where pages get redirected
        - lang: language data to extract
        - df_articles: list of covid-related article

    Output : list of articles name
    '''
    S = requests.Session()

    url = "https://{}.wikipedia.org/w/api.php".format(lang)

    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "redirects"
    }
    try:
        #get request to get the article that redirect of title
        r = S.get(url=url, params=PARAMS)
        data = r.json()
        if data['query'].get('pages') is None:
            return []
        pages = data["query"]["pages"]
        res = []
        #iterate through dict to get the articles name
        for k, v in pages.items():
            if v.get("redirects") is not None:
                for re in v["redirects"]:
                    if re["title"] not in df_articles.values:
                        res.append(re["title"])
    except:
        print("Error request Redirection")
        res = []
    
    return res


def wiki_to_df_extract(languageCode, begin_date, end_date, df_covid_articles):
    '''
    Function to fetch the data using wikimedia api

    Inputs : 

        - languageCode : language data to extract
        - begin_date
        - end_date
        - df_covid_articles: list of Covid related articles
        
    Output : concatenated df
    '''
    #filter language we want to extract
    df_covid_articles_country = df_covid_articles.loc[df_covid_articles.project == "{}.wikipedia".format(languageCode)]['page']
    df_agg_country = pd.DataFrame()
    redirect_art_list = []
    #iterate through articles
    for page in df_covid_articles_country:
        #get list of depreciated articles
        redirect_art_list = get_redirect_articles(page, languageCode, df_covid_articles_country)
        redirect_art_list.append(page)
        for page in redirect_art_list:
            #getting name in url-friendly synthax
            page = page.replace(' ', '_')
            page = urllib.parse.quote(page)
            page = page.replace('/', """%2F""")
            page = page.replace('?', """%3F""")
            url = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{}.wikipedia.org/all-access/user/{}/daily/{}/{}'.format(languageCode,page, begin_date, end_date)
            #without head we get blocked from the api
            header = {'User-Agent' : 'Robin Debalme (academic project; robin.debalme@epfl.ch; https://github.com/epfl-ada/ada-2022-project-thedatadiggers22)'}
            try:
                #get request to get a json of the page views of the given period
                r = requests.get(url, headers = header).json()
            except:
                print("Error request Extract")
            #concat
            df_agg_country = json_to_df(r, df_agg_country)
    return df_agg_country.groupby(['timestamp'])['views'].sum().to_frame()



def get_pageviews_df(raw_pageview_df: pd.DataFrame, population_df: pd.DataFrame, country_dict: dict, start: str, end: str):
    '''
    Function to get the different pageviews dataset
    
    Inputs : 

        - raw_pageview_df : raw dataset from csv
        - population_df : raw population dataset from csv
        - country_dict : countries we are interested in with language code
        - start : start date (yyyy-mm-dd)
        - end : end date (yyyy-mm-dd)
        
    Output : df_pageviews, df_pageviews_cumul, df_pageviews100k, df_pageviews_cumul100k
    '''
    #inv_country_dict = {v: k for k, v in country_dict.items()}
    pageview_df_imp_country = raw_pageview_df[["date"] + list(country_dict.values())].set_index('date')
    df_pageviews = pageview_df_imp_country.loc[pageview_df_imp_country.index < end]
    df_pageviews = df_pageviews.loc[df_pageviews.index >= start]
    df_pageviews = df_pageviews.interpolate(method ='linear', limit_direction ='forward') 
    df_pageviews = df_pageviews.fillna(0)

    df_pageviews_cumul = df_pageviews.cumsum()

    COUNTRY_OWN_LANG_POP = {"Italy" : "it", "Russian Federation": "ru", "China": "zh", "Albania": "sq", 
    "Bangladesh": "bn", "Botswana": "tn", "Cambodia": "km", "Croatia": "hr", "Greece": "el", "Sweden": "sv", "Finland": "fi", "Norway": "no",
    "Malaysia": "ms", "Israel": "he", "Lithuania": "lt", "Serbia": "sr", "Slovak Republic": "sk", "Slovenia": "sl", "Turkiye": "tr",
    "Vietnam": "vi", "Bulgaria": "bg", "Czechia": "cs", "Denmark": "da", "Georgia": "ka", "Germany": "de", 
    "Hungary": "hu", "Iceland": "is", "Japan": "ja", "Kazakhstan": "kk", "Korea, Rep.": "ko", "Kyrgyz Republic": 'ky', "Netherlands": "nl", "Poland": "pl", 
    "Romania": "ro", "Tajikistan": "tg", "Thailand": "th", "Azerbaijan": "az", "Mongolia": "mn"}

    population_df = population_df[["Country Name", "2020"]]
    population_df = population_df.set_index("Country Name")
    population_df = population_df.transpose()
    population_df = population_df[list(COUNTRY_OWN_LANG_POP.keys())]
    population_df = population_df.rename(columns= COUNTRY_OWN_LANG_POP)
    population_df = population_df[list(country_dict.values())]

    df_pageviews_cumul100k = df_pageviews_cumul/population_df.values * 100000
    df_pageviews100k = df_pageviews/population_df.values * 100000
    return df_pageviews, df_pageviews_cumul, df_pageviews100k, df_pageviews_cumul100k

def get_cases_deaths_df(population_df: pd.DataFrame, country_dict: dict, start: str, end: str):
    '''
    Function to get the different COVID cases and deaths dataset
    
    Inputs : 

        - population_df : raw population dataset from csv
        - country_dict : countries we are interested in with language code
        - start : start date (yyyy-mm-dd)
        - end : end date (yyyy-mm-dd)

    Output : deaths, cases, deaths_cumul, cases_cumul, deaths100k, deaths100k_cumul, cases100k, cases100k_cumul
    '''
    
    ssl._create_default_https_context = ssl._create_unverified_context
    death_url = "https://github.com/owid/covid-19-data/blob/master/public/data/jhu/new_deaths.csv?raw=true" # Make sure the url is the raw version of the file on GitHub
    cases_url = "https://github.com/owid/covid-19-data/blob/master/public/data/jhu/new_cases.csv?raw=true"

    # Reading the downloaded content and turning it into a pandas dataframe
    deaths = pd.read_csv(death_url,index_col=0)
    cases = pd.read_csv(cases_url,index_col=0)
    deaths= deaths.interpolate(method ='linear', limit_direction ='forward') 
    cases = cases.interpolate(method ='linear', limit_direction ='forward') 
    deaths = deaths.fillna(0)
    cases = cases.fillna(0)
    #Keep only values between start and end
    deaths = deaths[deaths.index < end]
    cases = cases[cases.index < end]
    deaths = deaths[deaths.index >= start]
    cases = cases[cases.index >= start]

    deaths = deaths.rename(columns= country_dict)[country_dict.values()]
    cases = cases.rename(columns= country_dict)[country_dict.values()]

    deaths_cumul = deaths.cumsum()
    cases_cumul = cases.cumsum()
    
    COUNTRY_OWN_LANG_POP = {"Italy" : "it", "Russian Federation": "ru", "China": "zh", "Albania": "sq", 
    "Bangladesh": "bn", "Botswana": "tn", "Cambodia": "km", "Croatia": "hr", "Greece": "el", "Sweden": "sv", "Finland": "fi", "Norway": "no",
    "Malaysia": "ms", "Israel": "he", "Lithuania": "lt", "Serbia": "sr", "Slovak Republic": "sk", "Slovenia": "sl", "Turkiye": "tr",
    "Vietnam": "vi", "Bulgaria": "bg", "Czechia": "cs", "Denmark": "da", "Georgia": "ka", "Germany": "de", 
    "Hungary": "hu", "Iceland": "is", "Japan": "ja", "Kazakhstan": "kk", "Korea, Rep.": "ko", "Kyrgyz Republic": 'ky', "Netherlands": "nl", "Poland": "pl", 
    "Romania": "ro", "Tajikistan": "tg", "Thailand": "th", "Azerbaijan": "az", "Mongolia": "mn"}

    population_df = population_df[["Country Name", "2020"]]
    population_df = population_df.set_index("Country Name")
    population_df = population_df.transpose()
    population_df = population_df[list(COUNTRY_OWN_LANG_POP.keys())]
    population_df = population_df.rename(columns= COUNTRY_OWN_LANG_POP)
    population_df = population_df[list(country_dict.values())]

    deaths100k = deaths/population_df.values * 100000
    deaths100k_cumul = deaths_cumul/population_df.values * 100000
    cases100k = cases/population_df.values * 100000
    cases100k_cumul = cases_cumul/population_df.values * 100000

    return deaths, cases, deaths_cumul, cases_cumul, deaths100k, deaths100k_cumul, cases100k, cases100k_cumul

def trust_category(trust, nbr_category, country_dict):
    """
    Divide trust interval into nbr_category and label the countries

    Inputs:
        trust: type of trust dataset
        nbr_category
        country_dict: original country dict

    Output:
         country_dict_cat : country dict sepearated in categories
    """
    country_dict_ = country_dict.copy()
    country_dict_cat = {}
    min_trust = float(trust.min(axis=1))
    max_trust = trust.max(axis=1)
    
    delta = float((max_trust-min_trust))/nbr_category
    
    for j in list(country_dict_.keys()):
        country_trust = float(trust[country_dict_[j]])
        for i in range(nbr_category):
            if (country_trust >= min_trust + i*delta) & (country_trust < min_trust + (i+1)*delta):
                country_dict_cat.update({country_dict_[j]:i})
                country_dict_[j] = [country_dict_[j], i]
            elif (country_trust == (min_trust + (i+1)*delta)) & (i == (nbr_category-1)):
                country_dict_cat.update({country_dict_[j]:i})
                country_dict_[j] = [country_dict_[j], i]

    return  country_dict_cat 

def format_title(title, subtitle=None, subtitle_font_size=12, title_font_size= 20):
    title = f'<span style="font-size: {title_font_size}px;"><b>{title}</b></span>'
    if not subtitle:
        return title
    subtitle = f'<span style="font-size: {subtitle_font_size}px; line-height: 20%;">{subtitle}</span>'
    return f'{title}<br>{subtitle}'
    

def mapcharts_df(df, country_dict, interest):
    '''
    Function create dataframe used for mapcharts
    
    Input : 
        - df : raw dataframe for the mapchart
        - country_dict : dict of countries of interest
        - interest : scope of analysis deaths, pageviews or cases
    Output : df_mapchart
    '''
    # Empty dataframe for the map chart
    df_mapchart = pd.DataFrame({})
    # Reverse the dictionary to map language codes to country names
    inv_country_dict = {v: k for k, v in country_dict.items()}
    # Add exceptions for country names that differ from their language codes
    other_country_name = {
    "Russia": "Russian Federation",
    "Turkey":"Türkiye",
    "Vietnam" : "Viet Nam",
    "South Korea" : "Korea, Democratic People's Republic of"
    }
    # Iterate through each country build the correct dataframe for the mapchart
    for country in country_dict.keys():
        
        df_tmp = pd.DataFrame(df.rename(columns= inv_country_dict)[country])
        df_tmp = df_tmp.rename(columns= {country: interest})
        if (country in list(other_country_name.keys())):
            df_tmp['Country_code'] = [countries.get(other_country_name[country]).alpha3] * len(df)
        else:
            df_tmp['Country_code'] = [countries.get(country).alpha3] * len(df_tmp)
        df_tmp['date'] = df_tmp.index
        df_tmp['country'] = country

        df_tmp = df_tmp.iloc[::5,:]
        df_mapchart = pd.concat([df_mapchart, df_tmp], axis= 0)
    return df_mapchart

def mapcharts(df, color_serie, hover_serie, title, subtile= None, font_title= 16, font_subtile= 12, colorcode= 'Reds'):
    '''
    Function create mapcharts
    
    Input : 
        - df : data used for the plot
        - color_serie : variable indicated by color gradient
        - hover_serie : variable displayed when hover on
        - title
        - subtitle
        -font_title
        -font_subtile
        -colorcode : color code for the map
    Output : 
    '''
    #create a new map chart
    fig = px.choropleth(df, locations= "Country_code",
                        color= df[color_serie],
                        animation_frame= 'date',
                        hover_name= df[hover_serie], # column to add to hover information
                        range_color= [0,np.percentile(df[color_serie],99)],
                        color_continuous_scale= colorcode, 
                        title= format_title(title, subtile, font_subtile, font_title),
                        width= 700,
                        height= 700)

    #Update layout, menus and buttons options
    fig.update_layout(transition = {'duration': 2})
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 0 # buttons
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 0
    fig.layout.updatemenus[0].buttons[1].args[1]["frame"]["duration"] = 0
    fig.layout.updatemenus[0].buttons[1].args[1]["transition"]["duration"] = 1
    fig.layout.sliders[0].steps[0].args[1]["frame"]["duration"] = 0 # slider
    fig.layout.updatemenus[0].buttons[0].args[1]["visible"] = False

    #Zoom on specific part of the map
    fig.update_geos(
        center=dict(lon=80, lat=35),
        projection_type="mercator",
        lataxis_range=[-50,80], lonaxis_range=[-10, 230]
    )

    fig.show()
    fig.write_html("results_for_website/{}_mapchart.html".format(color_serie),default_width= 500, default_height= 500)

def get_race_bar_df(df):
    '''
    Function to put in form a dataframe to create the bar chart race video
    
    Input : 
        - df : raw dataframe for the race
    Output : df_br
    '''
    df_br = df.rename(columns= {v: k for k, v in get_country_dict('original').items()}).reset_index().rename(columns = {'index': 'Country'})
    df_br = df_br.drop('date', axis= 1)
    #taking the rolling sum monthly
    df_br = df_br.rolling(30, min_periods=1).sum()
    #pset index in date format again
    df_br['index']= df_br.reset_index()['index'].apply(lambda x: (pd.to_datetime('2020-01-22') + datetime.timedelta(days= x)))
    df_br = df_br[df_br['index'].dt.day==1]
    #format as period mm-yyyy
    df_br.index = df_br['index'].apply(lambda x: "{}-{}".format(x.month, x.year))
    df_br = df_br.drop('index', axis= 1)
    return df_br

def get_mobility_df(country_dict):
    '''
    Function to get the mobility dataset and classifies it into moving and covid category
    
    Input : 
        - country_dict : countries we are interested in
    Output : mobility_df
    '''
    data_folder = 'data_2/'
    #Download mobility and intervention files
    google_mobility = pd.read_csv(data_folder+'Global_Mobility_Report.csv.zip')

    #Change name of the columns
    categories = ["Retail and Recreations", "Grocery and Pharmacy", "Parks","Transit stations", "Workplace", "Residential"]
    google_mobility = google_mobility.rename(dict(zip(google_mobility.columns[8:],categories)), axis = 1)

    #Transform date string to datetime
    google_mobility['date'] = pd.to_datetime(google_mobility['date'])

    #Delete columns about region
    google_mobility = google_mobility.drop(google_mobility.iloc[:,2:7], axis = 1)

    #Keep same dates as for corona wikipedia pages
    google_mobility = google_mobility.loc[(google_mobility['date'] < "2020-08-01") & (google_mobility['date'] >= "2020-01-22")]

    #Regroup all data per country and per date and take the average
    mobility = google_mobility.groupby(["country_region_code","country_region","date"]).mean()

    #Keep only the country that we are interested in
    mobility = mobility[mobility.index.get_level_values('country_region').isin(list(country_dict.keys()))]

    # Group together Parks, Retail and Recreations, Transit stations and Workplace by taking the mean of them
    mobility['moving category'] = mobility[['Retail and Recreations', 'Parks', 'Transit stations', 'Workplace']].mean(axis=1)
    #Group together Grocey and Pharmacy and Residential by taking the mean of them
    mobility['covid category'] = mobility[['Grocery and Pharmacy', 'Residential']].mean(axis=1)

    return mobility