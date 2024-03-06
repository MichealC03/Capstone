from folium import PolyLine
import pandas as pd
import folium 
from folium import plugins
from flask import Flask, render_template, redirect, request
import pymongo
import os
from amadeus import Client, ResponseError
from analytics import getPrices

amadeus = Client(
    client_id= os.getenv("AMADEUS_API_KEY"),
    client_secret= os.getenv("AMADEUS_API_SECRET")
)

#Connect to mongo
databaseInfo = os.getenv("FLIGHT_MONGO_INFO")
client = pymongo.MongoClient(databaseInfo)

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

# Dictionary to store all the information about their fleet
fleetDict = {
    "A321-Neo": {"seats": 189, "economySeats": 128, "extraComfortSeats": 44, "firstClassSeats": 16, "numberOfPlanes": 18},
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
    Purpose: Route to the index and display the airport dictionary for the user to select what they want
    """
    return render_template('index.html', airportDict=airportDict)

@app.route('/end')
def end():
    """
    Purpose: Route to the end and display statistics from the last and previous runs
    """
    # Get the operating prices for the flights
    A321NEOdf = getPrices(userChoiceDf, fleetDict)

    

    # userChoiceDf['Seats Filled A321-NEO'] = int(round(Q2Load * fleetDict['A321-Neo']['seats']))
    # userChoiceDf['Seats Filled A330'] = int(round(Q2Load * fleetDict['A330']['seats']))
    # userChoiceDf['Seats Filled B787'] = int(round(Q2Load * fleetDict['B787']['seats']))

    # Get the operating cost per flight

    print(A321NEOdf)

    return render_template('end.html',A321NEOdf=A321NEOdf, fleetDict=fleetDict)

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


def matchHourRow(df, matchHour, path, airport, simHour, color, map, planeNum):
    """
    Purpose:
        To find the matching hour row. This will be used in placeMarker to get the path up to this point

    ARGS:
        df dataframe: this is the dataframe that stores the data pulled from Mongo. We are searching the hours in this function.
        matchHour int: the hour being searched in the database for
        path dataframe: this is the dataframe that stores the locations of points for the plane
        airport str: the airport this plane is frome
        simHour int: this is the hour the plane is in to its' flight
        color str: this is the color of the map that is placed corresponding to the flight that is taken off
        map folium map: this is the map that is seen on the website
    """
    #Make a first try bool
    firstAttempt = True

    #Find corresponding data with the hour point
    while True:
        print(matchHour)
        rowNum = df[df['hour'] == str(matchHour)].index
        #If match found then break by making rowNum equal to the first data point that matches with hour
        if not rowNum.empty:
            rowNum = rowNum[-1]
            break
        #Else than subtract one to find the last hour that we have as there wasn't data points for that hour
        else:
            #Not first attempt anymore
            firstAttempt = False

            #Take one off the sim hour just to show how many hours back we are showing later
            pastHour = simHour - 1

            #Match hour -1 to get the past point that was there
            matchHour = int(matchHour) - 1
            if matchHour < 10:
                matchHour = '0' + str(matchHour)

    
    rowNum = rowNum + 1

    #If first point
    if simHour == 0:
        folium.Marker(path[0], popup=f'Start of Flight from: {airport}!', icon=folium.Icon(color=color)).add_to(map)
    #If the last row is = to the length of the dataframe then the flight is complete!
    elif rowNum == len(path):
        folium.PolyLine(path[:rowNum], popup=f'Flight Number {planeNum} from: {airport} Complete!', color=color).add_to(map)
        folium.Marker(path[-1], popup=f'Flight Number {planeNum} from: {airport} Complete!', icon=folium.Icon(color=color)).add_to(map)
    #If flight still ongoing 
    else:
        #Make the line and if there is no match for the current hour (!firstAttempt) then make a marker as well to inform
        folium.PolyLine(path[:rowNum], popup=f'Departure Airport: {airport} Current Hour of Flight: {simHour}', color=color).add_to(map)
        if not firstAttempt:
            rowNum = rowNum - 1
            folium.Marker(path[rowNum], popup=f'Departure Airport: {airport}. Waiting for points! Last Hour Shown of Flight: {pastHour}', icon=folium.Icon(color=color)).add_to(map)
        
    return map

def placeMarker(df, airport, map, matchHour, planeNum, simHour):
    """
    Purpose: 
        To place the marker on the map for each airplane. This will get called in getFlightInfo

    ARGS:
        df dataframe: this is the dataframe with all the data from Mongo
        airport str: this is the airport that the plane is flying from
        map foliumMap: This is the map that is displayed to show points
        matchHour str: This is the hour that is matched to the hours in the database
        simHour int : the hour that the simulation is currently in
        hoursLong int : the amount of hours the flight is
    """
    #This is the path that the plane takes with locations
    path = df[['lat', 'lon']].values.tolist()

    #Colors array
    colorArr = ['blue', 'red', 'green', 'orange', 'purple']

    for flight in range(planeNum):
        if(simHour >= 3*flight):
            #Subtract 3 for matchHour as it starts 3 hours late
            newMatchHour = (int(matchHour) - (3 * flight))

            #Add a 0 if a single digit number to perform match
            if newMatchHour < 10:
                newMatchHour = '0' + str(newMatchHour)

            map = matchHourRow(df, newMatchHour, path, airport, simHour - (3*flight), colorArr[flight], map, flight + 1)

    return map

def getFlightInfo(simHour, userChoiceDf):
    """
    Purpose:
        Get the info for a flight that is incoming from one airport and exiting from another

    ARGS:
        simHour int : the hour that the simulation is currently in
        userChoiceDf dataframe: this is the setup that the user selected
    """

    #Make a connection to the db
    db = client["FlightPath"]
    flight = db["Flights"]

    #Make an instance of a map
    map = folium.Map(location=[30, -120], zoom_start=4, width=1400, height=600)

    #Return the data for each airport in the dictionary
    for airport,data in userChoiceDf.iterrows():
        #Get num of planes
        try:
            planeNum = userChoiceDf.loc[airport, 'numPlanesA321NEO'] + userChoiceDf.loc[airport, 'numPlanesA330'] + userChoiceDf.loc[airport, 'numPlanesB787']
        except KeyError:
            print(f"Error: Airport '{airport}' not found in the DataFrame.")

        #Query for the departure airport
        myquery = { "departure": airport }
        mydoc = flight.find(myquery)

        # Create a list to store the data
        data_list = []

        # Iterate through the return and append each document to the list
        for document in mydoc:
            flights = document.get("points", [])
            data_list.extend(flights)

        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(data_list)


        #Get the starting hour and add the hour of the simulation to the starting hour.
        #   This number matches the database hour. It doesn't necessarily correlate to the simulation hour that is shown above the map
        startHour = df['hour'].iloc[0]
        matchHour = (int(startHour) + simHour)

        #Add a 0 if a single digit number to perform match
        if matchHour < 10:
            matchHour = '0' + str(matchHour)

        # Place the marker for thus flight during this hour
        map = placeMarker(df, airport, map, matchHour, planeNum, simHour)

    return map

if __name__ == '__main__':
    app.run()