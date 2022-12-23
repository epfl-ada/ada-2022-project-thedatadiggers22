# Digital propagation of the COVID-19 pandemic

## Description of the different files
<ol align="justify">
    <li>wiki_data_loader.ipynb : TODO</li>
    <li>milestone3.ipynb : Notebook with all our investigation of the different datasets.</li>
    <li>helpers.py : File containing the different functions used for our analysis.</li>
</ol>

## Abstract 
<p align="justify">
It is reasonable to assume that Wikipedia searches reflect interest, as users must actively want to know more about a subject to search it on Wikipedia. Using this hypothesis, we seek to assess the “digital” propagation of the COVID-19 pandemic by looking at the pageview statistics of COVID-related pages across different languages and comparing this to the geographical propagation of the virus. Does any relation exist between these two propagations? Is it different depending on the country of interest?<br>

In a second stage, we interest ourselves to the relation existing between the digital propagation and the population of each country by analysing their mobility during the pandemic and the trust they had towards their government. Do interested populations trust their government more and does it reflect on their movement? 
</p>

## Research questions
<ol align="justify">
    <li>How did the physical propagation of the COVID-19 pandemic is related to the evolution of the Wikipedia pageviews? Does COVID relates pages are more searched during the waves of the disease propagation?</li>
    <li>Does the number of deaths has an impact on the mobility of each population?</li>
    <li>Will people that are more or less confident about their politics look more, or less at COVID-related Wikipedia pages? Does this reflect in their mobility during lockdowns?</li>
</ol>

## Datasets
<ol align="justify">
    <li><strong>Full CoronaWiki article list</strong>. We analyzed more countries that the dataset provided in the ADA course. Shay Nowick, Sr. Data Scientist at Wikimedia Foundation, provided us the full dataset: it contains all COVID-related article titles in 175 languages. The COVID-related articles were identified using the pagelinks to the articles "COVID-19" or "COVID-19 Pandemic". Before receiving the dataset, we started building a script to scrape all the information from Wikipedia. See the pipeline in "data_pipeline.ipynb". 
    Unlike the data provided in the course, we also consider depreciated articles that now redirect to new COVID-related articles. Indeed the original dataset was underestimating the number of page views by a factor of up to 10. Case study for french language (see in data_pipeline): the following 12 pages are obviously related to covid but not all of them are present in the list of covid articles because they are depreciated and now redirect to other pages. For example, "Pandémie de maladie à coronavirus de 2020" en France redirects to "Pandémie de COVID-19 en France". Not considering these pages and the views they generated can lead to a biased analysis of the interest for Covid-19.
    </li>  
    <p align = "center">
    <img src="https://i.postimg.cc/2y7fJWtP/picture-fr-pageviews-31-03-2020.png" data-canonical-src="picture-fr-pageviews-31-03-2020.png" width="450" height="331"/>
    <img src="https://i.postimg.cc/ZY8ZCkqV/redirect-example.png" data-canonical-src="https://postimg.cc/0Kj3KzPf" width="450" height="135"/>
    </p>
  
Also :
    <ul align="justify">
        <li>Languages with less than 10 articles and languages that are not specific to a country (ex. English, Spanish) will be removed in a second phase.</li>
        <li>We used the articles titles of this dataset to download all pageviews statistics using the Wikipedia REST API and thus create the dataset needed to answer our research questions.</li>
        <li>Our analysis spanned from 01-01-2020 to 31-07-2022 to get an overview of the entire epidemic.</li>
    </ul></li>
    <li><a href="https://www.google.com/covid19/mobility/"><strong>Google Mobility</strong></a>: Initially provided in the scope of the ADA course, this dataset contains a mobility score for every country categorized by 6 different places. We again did not use the dataset provided in the course but downloaded an enriched version directly from Google to include more countries.</li>
    <li><a href="https://ourworldindata.org/trust"><strong>Population Trust</strong></a>: We use this additional dataset which contains results of attitudial surveys for what share of people trust their government, journalists and science. We will focus on the countries analysed in this project and use this information to compare the differences in covid pageviews trends between these countries. 
    <li><a href="https://ourworldindata.org/explorers/coronavirus-data-explorer"><strong>COVID-19 Dataset</strong></a>: This dataset contains all information relative to the COVID-19 pandemic in the form of a timeseries per country. We only used the cases per country and the deaths per country.</li>
</ol>

## Methods

### 1. Data scraping, pre-processing and dataframes creation
<ul align="justify">
    <li>Define the country of interest for our analysis. Select only countries where the principal language is spoken by more than 75% of the population. 
    </li>
    <li>Dataset pageview_df: Dataset containing the pageview statistics for all COVID-related pages in about 38 languages after pre-processing. A weekly seasonal pattern can be found in the pageviews of every languages. 
    </li> 
    <li>Dataset mobility_df: Google mobility dataset from different countries. We will extract the data for our countries of interests in which we seek to analyze          the mobility behavior.
    </li>
    <li>Dataset trust_df: Percentage of the population per country that trusts politics, journalists and science.
    </li>
    <li>Datasets deaths, cases: datasets with COVID deaths and cases per country.
    </li>
    
</ul>

### 2. First visualizations of COVID cases, deaths and COVID-related pageviews
<ul align="justify">
    <li>Plots of the evolution of cases, deaths and pageviews.
    </li>
    <li>Creation of interactive maps of COVID cases, of COVID deaths and of COVID-related articles pageviews per country.
    </li>
    <li>Correlation analysis between the COVID death and the COVID-related articles pageviews time series.
    </li>
    <li>Regression analysis relating the log of the number of COVID deaths and COVID-related articles pageviews per country. We plot the evolution of the fitted line through the pandemic and analyse its slope. We separate then the countries that informed themselves to the other ones.
    </li>
</ul>

### 3. Investigation of mobility and trust in select countries
<ul align="justify">
    <li> Creation of an animated graph that link the mobility and the trust towards the government with the number of deaths and pageviews. 
    </li>
    <li>Investigate the trust_df to identify links between information seeking behavior and trust of the population towards their government or the scientific community with the same methods. Identify the relation between COVID deaths and the trust of the population towards their government.
    </li>
    <li>Question the mobility_df to identify links between trust and mobility during the covid period.
    </li>
</ul>

### 4. Analysis of specific countries
<ul align="justify">
    <li>Description of Germany, Italy and Thailand in term of their economy, their government and their population.
    </li>
    <li>Specific analysis of the different time series of interest for these countries. 
    </li>
    <li>Comparison between these countries and how the population react differently during this pandemic.
    </li>
</ul>

### 5. Site building and Datastory
<ul align="justify">
    <li>Creation of the site in HTML.
    </li>
    <li>Put every analysis together to create the different pages of our data story. 
    </li>
</ul>


## Timeline
Internal Milestones V1:
1. Week 9 : Milestone 2 deadline: scraping and data wrangling pipelines
2. Weeks 10 & 11 : Homework 2,
3. Week 12 : Mappings of the propagation done, begin analysis and deep-dive,
4. Week 13 : Deep-dive finished, begin to create website and write datastory,
5. Week 14 : Cleaning of code, proofread of writing and submission of project.

## Organisation within the team during the project
<p align="justify">
We are using ZenHub to create and track our issues effectively. As this project is about continuous exploration, we used the Kanban methodology. We discussed, prioritized, distributed, and reassessed the issues during our weekly meetings.
Team members were free to participate in all different tasks depending on priority of said tasks. General distribution was as follow:
<ol>
  <li>Data pipelines and data wrangling: Robin & Carl,</li>
  <li>Data visualization and analysis methods: Arthur & Charlotte & Robin,</li>
  <li>Data analysis: All,</li>
  <li>Trust dataset: Charlotte,</li>
  <li>Mobility dataset: Arthur,</li>
  <li>Building site: Carl,</li>
  <li>Final redaction: All.</li>
</ol>
</p>

## Data Story

<p align="justify">
Our data story representing our results can be found at the following link: <a href="https://carlo-pien.github.io/ada_project_site/index.html#page-top">Uncovering the Digital Transmission of COVID-19</a>.
</p>