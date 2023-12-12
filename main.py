from folium import PolyLine
import pandas as pd
import folium 
from folium import plugins
from flask import Flask, render_template, redirect, request
import pymongo
import os
from amadeus import Client, ResponseError

amadeus = Client(
    client_id= os.getenv("AMADEUS_API_KEY"),
    client_secret= os.getenv("AMADEUS_API_SECRET")
)

#Connect to mongo
client = pymongo.MongoClient("mongodb+srv://michealcallahan24:apple@capstone.8yr2tov.mongodb.net/")

#Dictionary with all airports that Hawaiian Airlines flies to
airportDict = {
"Austin": {"ICAO": "KAUS", "latitude": 30.2025, "longitude": -97.6650},
"Boston": {"ICAO": "KBOS", "latitude": 42.3641, "longitude": -71.0052},
"Vegas": {"ICAO": "KLAS", "latitude": 36.0840, "longitude": -115.1536},
"Long Beach": {"ICAO": "KLGB", "latitude": 33.8177, "longitude": -118.1516},
"Los Angeles": {"ICAO": "KLAX", "latitude": 33.9416, "longitude": -118.4085},
"Oakland": {"ICAO": "KOAK", "latitude": 37.7214, "longitude": -122.2208},
"Ontario": {"ICAO": "KONT", "latitude": 34.0551, "longitude": -117.6006},
"Phoenix": {"ICAO": "KPHX", "latitude": 33.4342, "longitude": -112.0080},
"Portland": {"ICAO": "KPDX", "latitude": 45.5898, "longitude": -122.5951},
"Sacramento": {"ICAO": "KSMF", "latitude": 38.6957, "longitude": -121.5908},
"San Diego": {"ICAO": "KSAN", "latitude": 32.7336, "longitude": -117.1897},
"San Francisco": {"ICAO": "KSFO", "latitude": 37.7749, "longitude": -122.4194},
"San Jose": {"ICAO": "KSJC", "latitude": 37.3541, "longitude": -121.9375},
"Seattle": {"ICAO": "KSEA", "latitude": 47.4502, "longitude": -122.3088}
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

    userChoiceDf['Flight Price'] = getPrices(userChoiceDf)
    
    return render_template('end.html',userChoiceDf=userChoiceDf)

@app.route('/process_form', methods=['POST'])
def process_form():
    """
    Purpose: Receive the input from the user and place what the user wants into the global var userChoiceDf
    """
    global userChoiceDf

    #Get the list of airports and make a dictionary of the num of airplanes
    selectedAiports = request.form.getlist('selectedAirports')
    numPlanes = {airport: int(request.form.get(f'numAirplanes[{airport}]', 0)) for airport in selectedAiports}

    #Create a df of what was submitted
    planesDf = pd.DataFrame.from_dict(numPlanes, orient='index')

    #Rename the first column numPlanes
    planesDf.columns = ['numPlanes'] + list(planesDf.columns[1:])

    #Merge with the original dictionary with the ICAO, and locations of airports
    originalDictDf = pd.DataFrame.from_dict(airportDict, orient='index')
    userChoiceDf = pd.merge(originalDictDf, planesDf, left_index=True, right_index=True)

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

def getPrices(df):
    """
    Purpose:
        Return a list of prices for the flights total profit

    ARGS:
        df dataframe: This is the dataframe that the user chose to simulate
    """
    priceList = []

    #For each airport in df get the price
    for airport,data in df.iterrows():
        #Remove the K from ICAO
        airportInitials = df.loc[airport, 'ICAO']
        airportInitials = airportInitials[1:]

        #Get plane Num for that airport in the simulation
        planeNum = userChoiceDf.loc[airport, 'numPlanes']

        #Get best offer for the flight
        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=airportInitials, 
                destinationLocationCode='HNL',
                departureDate='2024-01-11',
                returnDate='2024-01-18',
                adults=2,
                currencyCode="USD"
                )
            first_offer = response.data[0]
            price = first_offer['price']['grandTotal']

            #Multiply times number of planes
            price = float(price) * planeNum

            priceList.append("{:.2f}".format(float(price)))
        except ResponseError as error:
            print(error)

    return priceList


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

    #If first point
    if simHour == 0:
        folium.Marker(path[0], popup=f'Start of Flight from: {airport}!', icon=folium.Icon(color=color)).add_to(map)
    #If the last row is = to the length of the dataframe then the flight is complete!
    elif rowNum + 1 == len(path):
        folium.PolyLine(path[:rowNum], popup=f'Flight Number {planeNum} from: {airport} Complete!', color=color).add_to(map)
        folium.Marker(path[-1], popup=f'Flight Number {planeNum} from: {airport} Complete!', icon=folium.Icon(color=color)).add_to(map)
    #If flight still ongoing 
    else:
        #Make the line and if there is no match for the current hour (!firstAttempt) then make a marker as well to inform
        folium.PolyLine(path[:rowNum], popup=f'Departure Airport: {airport} Current Hour of Flight: {simHour}', color=color).add_to(map)
        if not firstAttempt:
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
            planeNum = userChoiceDf.loc[airport, 'numPlanes']
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