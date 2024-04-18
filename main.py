import pandas as pd
from flask import Flask, render_template, redirect, request, session
import pymongo
import os
from amadeus import Client, ResponseError
from analytics import getPrices, getPreset, getPricesPreset, getTotalsPreset
from flightMap import getFlightInfo

amadeus = Client(
    client_id= os.getenv("AMADEUS_API_KEY"),
    client_secret= os.getenv("AMADEUS_API_SECRET")
)

#Dictionary with all airports that Hawaiian Airlines flies to
airportDict = {
"Austin": {"ICAO": "KAUS", "latitude": 30.2025, "longitude": -97.6650, "miles": 3750},
"Boston": {"ICAO": "KBOS", "latitude": 42.3641, "longitude": -71.0052, "miles": 5085},
"Vegas": {"ICAO": "KLAS", "latitude": 36.0840, "longitude": -115.1536, "miles": 2751},
"Long Beach": {"ICAO": "KLGB", "latitude": 33.8177, "longitude": -118.1516, "miles": 2494},
"Los Angeles": {"ICAO": "KLAX", "latitude": 33.9416, "longitude": -118.4085, "miles": 2556},
"Oakland": {"ICAO": "KOAK", "latitude": 37.7214, "longitude": -122.2208, "miles": 2397},
"Ontario": {"ICAO": "KONT", "latitude": 34.0551, "longitude": -117.6006, "miles": 2512},
"Phoenix": {"ICAO": "KPHX", "latitude": 33.4342, "longitude": -112.0080, "miles": 2883},
"Portland": {"ICAO": "KPDX", "latitude": 45.5898, "longitude": -122.5951, "miles": 2674},
"Sacramento": {"ICAO": "KSMF", "latitude": 38.6957, "longitude": -121.5908, "miles": 2560},
"San Diego": {"ICAO": "KSAN", "latitude": 32.7336, "longitude": -117.1897, "miles": 2614},
"San Francisco": {"ICAO": "KSFO", "latitude": 37.7749, "longitude": -122.4194, "miles": 2397},
"San Jose": {"ICAO": "KSJC", "latitude": 37.3541, "longitude": -121.9375, "miles": 2403},
"Seattle": {"ICAO": "KSEA", "latitude": 47.4502, "longitude": -122.3088, "miles": 2677},
"New York City": {"ICAO": "KJFK", "latitude": 40.6413, "longitude": -73.7781, "miles": 4982}
}

# Dictionary of a preset fleet that Hawaiian Airlines has
airportDictPreset = {
    "Austin": {"ICAO": "KAUS", "A321": 0, "A330": 1, "B787": 0},
    "Boston": {"ICAO": "KBOS", "A321": 0, "A330": 1, "B787": 0},
    "Vegas": {"ICAO": "KLAS", "A321": 1, "A330": 3, "B787": 0},
    "Long Beach": {"ICAO": "KLGB", "A321": 1, "A330": 0, "B787": 0},
    "Los Angeles": {"ICAO": "KLAX", "A321": 2, "A330": 4, "B787": 1},
    "Oakland": {"ICAO": "KOAK", "A321": 2, "A330": 1, "B787": 0},
    "Ontario": {"ICAO": "KONT", "A321": 1, "A330": 0, "B787": 0},
    "Phoenix": {"ICAO": "KPHX", "A321": 0, "A330": 1, "B787": 1},
    "Portland": {"ICAO": "KPDX", "A321": 1, "A330": 1, "B787": 0},
    "Sacramento": {"ICAO": "KSMF", "A321": 1, "A330": 1, "B787": 0},
    "San Diego": {"ICAO": "KSAN", "A321": 1, "A330": 1, "B787": 0},
    "San Francisco": {"ICAO": "KSFO", "A321": 1, "A330": 1, "B787": 0},
    "San Jose": {"ICAO": "KSJC", "A321": 1, "A330": 1, "B787": 0},
    "Seattle": {"ICAO": "KSEA", "A321": 0, "A330": 2, "B787": 0},
    "New York City": {"ICAO": "KJFK", "A321": 0, "A330": 1, "B787": 0}
}

# Dictionary to store all the information about their fleet
fleetDict = {
    "A321NEO": {"seats": 189, "economySeats": 128, "extraComfortSeats": 44, "firstClassSeats": 16, "numberOfPlanes": 18},
    "A330": {"seats": 278, "economySeats": 200, "extraComfortSeats": 60, "firstClassSeats": 18, "numberOfPlanes": 24},
    "B787": {"seats": 300, "economySeats": 187, "extraComfortSeats": 79, "firstClassSeats": 34, "numberOfPlanes": 2},
    "B717": {"seats": 128, "economySeats": 128, "extraComfortSeats": 0, "firstClassSeats": 8, "numberOfPlanes": 120},
}

#Df with the choices of the user and what their airports they want to fly from are
userChoiceDf = None

app = Flask(__name__)

@app.route('/')
def index():
    """
    Purpose: Route to the index and display the airport dictionary with preset filled out
    """
    return render_template('index.html', airportDict=airportDict)

@app.route('/index_preset')
def indexPreset():
    """
    Purpose: Route to the index and display the airport dictionary for the user to select what they want
    """
    return render_template('indexPreset.html', airportDict=airportDictPreset)

@app.route('/analytics_Factors')
def factors():
    return render_template('analyticsFactors.html')

@app.route('/submit_load_factor', methods=['POST'])
def submit_load_factor():
    load_factor = request.form['factor_load_percentage_input']
    CASM = request.form['operating_cost_per_available_seat_mile_input']
    extraComfort = request.form['extra_comfort_multiplier']
    firstClass = request.form['first_class_multiplier']
    return redirect('/end?load_factor={}&CASM={}&extraComfort={}&firstClass={}'.format(load_factor, CASM, extraComfort, firstClass))

@app.route('/preset_end')
def presetEnd():
    """
    Purpose: 
        Route to the end and display statistics from a preset
    """

    # Retrieve load factor and CASM from request parameters
    load_factor = request.args.get('load_factor')
    CASM = request.args.get('CASM')
    extraComfort = request.args.get('extraComfort')
    firstClass = request.args.get('firstClass')

    # Get the preset details
    A321NEOdf = getPreset("A321Neo")
    A330df = getPreset("A330")
    B787df = getPreset("B787")

    # Convert the CASM, extraComfort, and firstClass to floats
    CASM = float(CASM) / 100
    extraComfort = float(extraComfort)
    firstClass = float(firstClass)

    # Get the operating prices, total profit, and net revenue for the flights preset
    A321NEOdf = getPricesPreset(A321NEOdf, airportDict, CASM, extraComfort, firstClass)
    A330df = getPricesPreset(A330df, airportDict, CASM, extraComfort, firstClass)
    B787df = getPricesPreset(B787df, airportDict, CASM, extraComfort, firstClass)

    # merge all the dataframes to get the total profit and net revenue
    totalDf = pd.concat([A321NEOdf, A330df, B787df]).reset_index(drop=True)

    totalDf = getTotalsPreset(totalDf)
    

    return render_template('endPreset.html',A321NEOdf=A321NEOdf, A330df = A330df, B787df = B787df, totalDf = totalDf, extraComfortMult= extraComfort, firstClassMult=firstClass)

@app.route('/end')
def end():
    """
    Purpose: Route to the end and display statistics from the last and previous runs
    """

    # Retrieve load factor and CASM from request parameters
    load_factor = request.args.get('load_factor')
    CASM = request.args.get('CASM')
    extraComfort = request.args.get('extraComfort')
    firstClass = request.args.get('firstClass')

    # Get the operating prices for the flights
    A321NEOdf, A330df, B787df, totalDf = getPrices(userChoiceDf, fleetDict, float(load_factor), float(CASM), float(extraComfort), float(firstClass))

    return render_template('end.html',A321NEOdf=A321NEOdf, A330df = A330df, B787df = B787df, totalDf = totalDf, load_factor = float(load_factor), CASM = float(CASM), extraComfortMult=float(extraComfort), firstClassMult=float(firstClass))

@app.route('/process_form', methods=['POST'])
def process_form():
    """
    Purpose: Receive the input from the user and place what the user wants into the global var userChoiceDf
    """
    global userChoiceDf

    #Get the list of airports and make a dictionary of the num of airplanes
    selectedAiports = request.form.getlist('selectedAirports')
    numPlanesA321NEO = {airport: int(request.form.get(f'numAirplanesA321NEO[{airport}]', 0)) for airport in selectedAiports}
    numPlanesA330 = {airport: int(request.form.get(f'numAirplanesA330[{airport}]', 0)) for airport in selectedAiports}
    numPlanesB787 = {airport: int(request.form.get(f'numAirplanesB787[{airport}]', 0)) for airport in selectedAiports}

    #Create a df of what was submitted
    planesDf = pd.DataFrame([numPlanesA321NEO, numPlanesA330, numPlanesB787]).T

    #Rename the columns
    planesDf.columns = ['numPlanesA321NEO', 'numPlanesA330', 'numPlanesB787']
    
    # Drop columns that have 0 all across
    planesDf = planesDf.loc[~(planesDf[['numPlanesA321NEO', 'numPlanesA330', 'numPlanesB787']] == 0).all(axis=1)]

    #Merge with the original dictionary with the ICAO, and locations of airports
    originalDictDf = pd.DataFrame.from_dict(airportDict, orient='index')
    userChoiceDf = pd.merge(originalDictDf, planesDf, left_index=True, right_index=True)

    # If planesDf is empty, then redirect to the index
    if planesDf.empty:
        # If planesDf is empty, then redirect to the index
        if planesDf.empty:
            return redirect('/')

    # Redirect to the review template
    return render_template('success.html', planesDf=planesDf)

#Display the map
@app.route('/add_marker/<int:hour>', methods=['GET'])
def add_marker(hour):
    """
    Purpose: 
        Add the markers for where each plane is at every hour 
    """
    global userChoiceDf

    #Call this method in order to get the updated map for the hour
    map = getFlightInfo(hour, userChoiceDf)

    #Get the different parts of the map to put it into html
    map.get_root().render()
    header = map.get_root().header.render()
    mapBody = map.get_root().html.render()
    script = map.get_root().script.render()

    return render_template('display.html', header=header, mapBody=mapBody, script=script, hour=hour, next_hour= hour + 1)


if __name__ == '__main__':
    app.run()