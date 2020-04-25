from flask import Flask, render_template, request
import requests
import csv
import sys


app = Flask(__name__)

# main source https://github.com/nytimes/covid-19-data
url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

def get_data(url):
    r = requests.get(url)
    content = r.content.decode('utf-8')
    raw_datalist = content.splitlines()
    return raw_datalist

def find_county(county, raw_datalist):
    county_data = []
    for line in raw_datalist: 
        if county in line:
            county_data.append(line)
    return county_data

def latest_date_available(county_data):
    county_data = county_data[-1].split(',')
    return county_data[0]

def find_county_by_date(county_data, inputdate):
    for line in county_data:
        if inputdate in line:
            today = line
        else:
            today = False
    if today:
        today = today.split(',')
    return today

def list_dates(county_data):
    dates_list = []
    for line in county_data:
        str_line = str(line)
        x = str_line.split(',')
        dates_list.append(x[0])
    return dates_list

def list_infections(county_data):    
    infections_list = []
    for line in county_data:
        str_line = str(line)
        y = str_line.split(',')
        infections_list.append(y[-2])
    return infections_list

def show_numbers(dates, infections):
    numbers = dict(zip(dates, infections))
    return numbers

def calc_infection_rate(values):
    output = [0.0]
    startpos, endpos = (1, len(values)-1)
    while True:
        current = int(values[startpos])
        previous = int(values[startpos-1])
        ret = 100*((current-previous)/(1.0*previous))
        output.append(round(ret,2))
        startpos += 1
        if startpos > endpos:
            break
    return output

@app.route('/')
def main():
    return render_template('main_form.html/')

@app.route('/', methods=['POST'])
def main_post():
    county_input = request.form['county_input']

    # clean the input
    county_input = county_input.strip()
    county_input = county_input.title()
    cityname_corrections = {
            'New York':'New York City',
            'Ny':'New York City',
            'Nyc':'New York City',
            'Dc':'District of Columbia',
            'Washington Dc':'District of Columbia',
            'Sf':'San Francisco',
            'San Fran':'San Francisco'
            }
    if county_input in cityname_corrections:
        county_input = cityname_corrections[county_input]

    # encapsulate keyword with cammas as markers for complete city name
    county = county_input
    comma_county = ',' + county_input + ','

    # get data from csv
    raw_data = get_data(url)

    # test to see if county is found in dataset first
    keyword_test = True
    for i in raw_data:
        if comma_county in i:
            keyword_test = True
            break
        else:
            keyword_test = False
    if not keyword_test:
        return render_template('error.html/', county=county)

    # find comma_county and list all iterations
    county_data = find_county(comma_county, raw_data)

    # extract date from county_data for dates / infections iterations
    dates = list_dates(county_data)
    infections = list_infections(county_data)
    
    # calculate infection rate change from previous day
    infection_rate = calc_infection_rate(infections)

    # most current iteration with stats
    todays_numbers = find_county_by_date(county_data, latest_date_available(county_data))
    todays_infected = todays_numbers[-2]
    todays_deaths = todays_numbers[-1]

    # iterate through date, infections, infection rate) and list it within a list
    index = 0
    full_list = []
    for i in range(len(dates)):
        full_list.insert(0, [dates[i], infections[i], infection_rate[i]])
        index += 1


    return render_template('main_post.html/', infections=infections, dates=dates, infection_rate=infection_rate, county=county, todays_infected=todays_infected, todays_deaths=todays_deaths, full_list=full_list)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)