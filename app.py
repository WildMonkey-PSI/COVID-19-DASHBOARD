import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

global start 
start = time.time()

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

global data_csv
data_csv = pd.read_csv('https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv')

def setSelectorsToDropDown(data_csv):
    countries_all = []
    for x in data_csv['Country/Region']:
        countries_all.append(x)
    countries_all = list(dict.fromkeys(countries_all)) 
    countries = []
    for x in countries_all:
        countries.append({'label': x, 'value': x})
    return countries

def selectAllCountriesToList(data_csv):
    countries_all = []
    for x in data_csv['Country/Region']:
        countries_all.append(x)
    countries_all = list(dict.fromkeys(countries_all)) 
    countries = []
    for x in countries_all:
        countries.append(x)
    return countries

def countAllCasesForCountries(countries):
    sum = {}
    for x in countries:
        index = np.where(data_csv == x)
        tup  = index[0]
        all = 0
        for y in tup:
            all += data_csv.iloc[y,-1]
        sum[x] = all
    sum = sorted(sum.items(), key=lambda x: x[1], reverse=True)
    sum = np.array(sum)
    return sum

def countAllCasesForOneCountry(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    allCases = []
    for x in dates[3:]:
        countryRows = country.value.loc[country.variable == x]
        all = 0
        for y in countryRows:
            all += y
        allCases.append(all)  
    return allCases

def selectDates(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    datesArray = []
    for x in dates[3:]:
        split = (x.split("/"))
        buildedDate = datetime(int("20"+split[2]),int(split[0]),int(split[1]))
        datesArray.append(buildedDate)
    return datesArray

def countAllCasesPerDayForOneCountry(name):
    country_data = data_csv.loc[data_csv['Country/Region'] == name]
    country = country_data.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]
    yesterday = 0
    allCasesPerDayArray = []
    for x in dates[3:]:
        countryRows = country.value.loc[country.variable == x]
        all = 0
        for y in countryRows:
            all += y
        allCasesPerDayArray.append(all - yesterday)
        yesterday = all  
    return allCasesPerDayArray

def countLastCasesPerDayForOneCountry(name):
    countryData = data_csv.loc[data_csv['Country/Region'] == name]
    country = countryData.melt(id_vars=['Country/Region'])
    country = country[3::]
    dates = country.variable.drop_duplicates()
    dates = dates[3:]

    yesterdayRows = dates[len(dates)-2:len(dates)-1]
    yesterdayRows = list(yesterdayRows.items())[0][1]
    yesterdayCountryRows = country.value.loc[country.variable == yesterdayRows]
    all = 0
    for y in yesterdayCountryRows:
        all += y
    yesterday = all

    todayRows = dates[len(dates)-1:len(dates)]
    todayRows = list(todayRows.items())[0][1]
    todayCountryRows = country.value.loc[country.variable == todayRows]
    all = 0
    for y in todayCountryRows:
        all += y
    today = all

    return today - yesterday

def countAllData():

    global countries
    global total_rank
    global data_csv
    global countedCasesAllCountriesPerDayReversed
    global countedCasesAllCountriesPerDay
    global leastCasesPerDay
    global countriesWithoutDisease
    
    data_csv = pd.read_csv('https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv&filename=time_series_covid19_confirmed_global.csv')
    #data_csv = pd.read_csv('C:\\Users\\kucza\\Downloads\\time_series_covid19_confirmed_global (1).csv')

    countries = selectAllCountriesToList(data_csv)
    total_rank = countAllCasesForCountries(countries)
    dic = {}
    for country in countries:
        dic[country] = countLastCasesPerDayForOneCountry(country)
    
    countedCasesAllCountriesPerDay = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    countedCasesAllCountriesPerDayReversed = sorted(dic.items(), key=lambda x: x[1])

    leastCasesPerDay = {}
    countriesWithoutDisease = 0
    for x in countedCasesAllCountriesPerDayReversed:
        
        if(x[1] > 0):
            leastCasesPerDay[x[0]] = x[1]
            break
        countriesWithoutDisease+=1

countAllData()

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(children=[
    html.H1("COVID-19 DASHBOARD - Python version", style={'textAlign': 'center'}),
    html.Div([
        html.B(id = 'liveUpdate'),
        html.A(html.Button(id ='button')),
        html.Div(id = 'initDiv')],
        id = 'dataDiv'),
    html.Div([
        html.Div(id = 'firstDiv'),
        html.Div(id = 'secondDiv'),
        html.Div(id = 'thirdDiv')],
        id = "basicData"),
    dcc.Graph(
        id = "top5Plot"
    ),
    html.Div("Wybierz Kraj:", style={'paddingBottom':'1%','paddingLeft':'5%'}),
    dcc.Dropdown(
        id='dropDownList',
        options=setSelectorsToDropDown(data_csv),
        value=['Poland'],
        style={'width':'40%'},
        multi = True 
    ),
    dcc.Graph(
        id='lineChart',
    ),
    dcc.Graph(
        id='barPlot',
    ),
])

@app.callback(
     [dash.dependencies.Output('top5Plot', 'figure')],
     [dash.dependencies.Input('firstDiv', 'children')])
def update_outputt(n_clicks):
    figure={
            'data': [
                {'x': total_rank[:5,0], 'y': total_rank[:5,1], 'type': 'bar', 'name': 'SF'},
            ],
            'layout': {
                'title': 'Kraje z największą liczbą przypadków zakażeń',
            },
    }
    return [figure]



@app.callback(
    [dash.dependencies.Output('initDiv', 'children')],
    [dash.dependencies.Input('button', 'n_clicks')])

def update_outputt(n_clicks):
    global start
    start = time.time()
    return [html.Div()]


@app.callback(
    [dash.dependencies.Output('basicData', 'children')],
    [dash.dependencies.Input('initDiv', 'children')])

def update_outputty(n_clicks):

    return [html.Div([
        html.Div(id = 'firstDiv'),
        html.Div(id = 'secondDiv'),
        html.Div(id = 'thirdDiv')],style={'visibility':'visible'})]
        
@app.callback(
    [dash.dependencies.Output('firstDiv', 'children')],
    [dash.dependencies.Output('secondDiv', 'children')],
    [dash.dependencies.Output('thirdDiv', 'children')],
    [dash.dependencies.Output('liveUpdate', 'children')],
    [dash.dependencies.Output('button', 'children')],
    [dash.dependencies.Input('initDiv', 'children')])

def update_outputty(n_clicks):
    countAllData()
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    return [html.Div([
        "Odnotowano najwięcej przypadków zakażeń w kraju: " ,
        html.B("{}".format(countedCasesAllCountriesPerDay[0][0])), 
        " z liczbą ",
        html.B("{}".format(countedCasesAllCountriesPerDay[0][1])), 
        " przypdaków"], style={'textAlign':'center', 'visibility':'visible'})
        ],[html.Div([
        "Odnotowano najmniej przypadków zakażeń w kraju: " ,
        html.B("{}".format(list(leastCasesPerDay.items())[0][0])),
        " z liczbą ",
        html.B("{}".format(list(leastCasesPerDay.items())[0][1])),
        " przypdaków"], style={'textAlign':'center', 'visibility':'visible'})
        ],[html.Div([
        "Nie odnotowano nowych przypadków w ",
        html.B("{}".format(countriesWithoutDisease)),
        " krajach"
        ], style={'textAlign':'center', 'visibility':'visible', 'paddingBottom':'3%'})
        ],[html.B(str(dt_string)+" ",style={'textAlign':'center'})
        ],[html.Button("Odśwież dane",style={'visibility':'visible'} , id='button')]


@app.callback(
    [dash.dependencies.Output('dataDiv', 'children')],
    [dash.dependencies.Input('button', 'n_clicks')])

def update_outputt(n_clicks):
    return [html.Div([
    "Dane pobrano: ", 
    html.B("ładowanie aktualnych danych...",id = "liveUpdate"),
    html.A(html.Button("Odśwież dane",style={'visibility':'hidden'}, id="button")),
    html.Div(id = 'initDiv')],
    style={'textAlign':'center'}, id = 'dataDiv')]
    
@app.callback(
    [dash.dependencies.Output('dropDownList', 'value')],
    [dash.dependencies.Input('initDiv', 'children')])
    
def update_outputt(n_clicks):
    return [['Poland']]
 
@app.callback(
    [dash.dependencies.Output('lineChart', 'figure'),
    dash.dependencies.Output('barPlot', 'figure')],
    [dash.dependencies.Input('dropDownList', 'value')])

def update_output(value):

    plot_x = selectDates('Poland')
    selectedCountries = ""
    figure = go.Figure()
    for country in value:
        selectedCountries += ", " + str(country).strip("['']") 
        plo =  countAllCasesForOneCountry(str(country).strip("['']"))
        figure.add_trace(go.Scatter(x=plot_x,y= plo,name = str(country).strip("['']"),marker = dict(line=dict(width = 0))))
    
    figure1 = go.Figure()
    for country in value:
        plo = countAllCasesPerDayForOneCountry(str(country).strip("['']"))
        figure1.add_trace(go.Bar(x=plot_x,y= plo,name = str(country).strip("['']")))

    figure.update_layout(template="plotly_white",title =  {'text':'Wszystkie przypadki dla' + selectedCountries.lstrip(','),'x':0.5})
    figure1.update_layout(template="plotly_white",barmode='stack',title = {'text' : 'Dobowy przyrost dla' + selectedCountries.lstrip(','),'x':0.5})

    return figure,figure1

end = time.time()

if __name__ == '__main__':
    app.run_server("127.0.0.1")
