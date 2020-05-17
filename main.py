# Quick stats for local COVID-19 / Coronavirus stats by local county
# https://github.com/rapidlee/covid19quicksearch


from flask import Flask, render_template, request, session
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
    duplicate_county = bool
    state = False

    # if state_select has a value, POST is coming from duplicates.html
    if request.form.get('state_select'):
        duplicate_county = True
        county_input = request.form['county1']
        state = request.form['state_select']
        # search paramter now should include state to identify county appropriately 
        comma_county_state = ',' + county_input + ',' + state
    else:
        county_input = request.form.get('county_input')
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

    # encapsulate keyword with cammas as markers for complete county name
    county = county_input
    
    # test if coming from duplicates.html, if so we change the search parameter to include state
    if duplicate_county == True:
        comma_county = comma_county_state
    else:
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
    # print(*county_data, file=sys.stdout, sep='\n')
    
    # list of lists results by county
    full_county_list = list_by_county(county_data)
    # print(*full_county_list, file=sys.stdout, sep='\n')

    # Test for duplicates
    compare_duplicates = [x[2] for x in full_county_list]
    if len(set(compare_duplicates)) != 1:
        print('We found multple states with the same county name', file=sys.stdout)
        list_of_states = set(compare_duplicates)
        return render_template('duplicates.html/', list_of_states=list_of_states, county=county)



    # assign final numbers
    dates = [x[0] for x in full_county_list]
    infections = [x[-2] for x in full_county_list]
    infection_rate = calc_infection_rate(infections)
    todays_infected = full_county_list[-1][-2]
    todays_deaths = full_county_list[-1][-1]

    #iterate through date, infections, infection rate and list it within a list
    display_list = []
    for i in range(len(dates)):
        display_list.insert(0, [dates[i], infections[i], infection_rate[i]])

    return render_template('main_post.html/', county=county, todays_infected=todays_infected, todays_deaths=todays_deaths, display_list=display_list, state=state)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)