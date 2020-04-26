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

def find_county(county, raw_data_list):
    county_data = []
    for line in raw_data_list: 
        if county in line:
            county_data.append(line)
    return county_data

def list_by_county(county_data):
    county_list = []
    for line in county_data:
        elements = line.split(',')
        county_list.append(elements)
    # print(*test_list, sep='\n')
    return county_list

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

    # list of lists results by county
    full_county_list = list_by_county(county_data)

    dates = [x[0] for x in full_county_list]
    infections = [x[-2] for x in full_county_list]
    infection_rate = calc_infection_rate(infections)
    todays_infected = full_county_list[0][-2]
    todays_deaths = full_county_list[0][-1]

    #iterate through date, infections, infection rate) and list it within a list
    display_list = []
    for i in range(len(dates)):
        display_list.insert(0, [dates[i], infections[i], infection_rate[i]])

    return render_template('main_post.html/', county=county, todays_infected=todays_infected, todays_deaths=todays_deaths, display_list=display_list)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)