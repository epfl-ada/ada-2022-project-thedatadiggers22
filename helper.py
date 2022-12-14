import pandas as pd
import requests
import urllib

COUNTRY_OWN_LANG = {"Italy" : "it", "Russia": "ru", "China": "zh", "Albania": "sq", 
"Bangladesh": "bn", "Botswana": "tn", "Cambodia": "km", "Croatia": "hr", "Greece": "el", "Sweden": "sv", "Finland": "fi", "Norway": "no",
 "Malaysia": "ms", "Israel": "he", "Lithuania": "lt", "Serbia": "sr", "Slovakia": "sk", "Slovenia": "sl", "Turkey": "tr",
 "Vietnam": "vi", "Bulgaria": "bg", "Czechia": "cs", "Denmark": "da", "Georgia": "ka", "Germany": "de", 
 "Hungary": "hu", "Iceland": "is", "Japan": "ja", "Kazakhstan": "kk", "South Korea": "ko", "Kyrgyzstan": 'ky', "Netherlands": "nl", "Poland": "pl", 
 "Romania": "ro", "Tajikistan": "tg", "Thailand": "th", "Azerbaijan": "az", "Mongolia": "mn"}
 
def get_country_dict():
    return COUNTRY_OWN_LANG


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