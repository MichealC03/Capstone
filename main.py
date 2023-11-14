from pyopensky.impala import Impala
import matplotlib.pyplot as plt
from folium import PolyLine
import pandas as pd
import folium 
from folium import plugins
from flask import Flask, render_template, redirect, request
import pymongo

# Create an instance of the Impala class with authentication credentials
opensky = Impala(
    username="MCallahan03",
    password="Soccer21!",
    host="data.opensky-network.org",
    port=2230  # The port for the Impala shell
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

app = Flask(__name__)

@app.route('/')
def show_map():
    return render_template('index.html', airportDict=airportDict)

@app.route('/process_form', methods=['POST'])
def process_form():
    selected_airports = request.form.getlist('selectedAirports')
    num_airplanes = {airport: int(request.form.get(f'numAirplanes[{airport}]', 0)) for airport in selected_airports}

    # Now you can use 'selected_airports' and 'num_airplanes' in your Python code
    # For example, print them for demonstration purposes
    print('Selected Airports:', selected_airports)
    print('Number of Airplanes:', num_airplanes)

    # Add your processing logic here

    # Redirect or render another template as needed
    return render_template('success.html')  # Replace with your desired template

@app.route('/add_marker/<int:hour>', methods=['GET'])
def show_map_by_distance(hour):

    m = getFlightInfo(hour)
    m.get_root().render()
    header = m.get_root().header.render()
    mapBody = m.get_root().html.render()
    script = m.get_root().script.render()

    if hour == 10:
        return render_template('index.html', airportDict=airportDict)
    else:
        return render_template('display.html', header=header, mapBody=mapBody, script=script, hour=hour, next_hour= hour + 1)


def getFlightInfo(hour):
    """Get the info for a flight that is incoming from one airport and exiting from another

    ARGS:
        hour int : get the hour that should be searched for
    """

    #Make a connection to the db
    db = client["FlightPath"]
    flight = db["Flights"]

    #Make an instance of a map
    m = folium.Map(location=[30, -120], zoom_start=4, width=1400, height=600)

    #Return the data for each airport in the dictionary
    for airport,data in airportDict.items():
        #Query for all airports with that departure
        myquery = { "departure": airport }
        mydoc = flight.find(myquery)

        # Create a list to store the data
        data_list = []

        # Iterate through the cursor and append each document to the list
        for document in mydoc:
            flights = document.get("points", [])
            data_list.extend(flights)

        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(data_list)

        #Get starting day and make a day col
        startDay = df['day'].iloc[0]

        #Get starting and current hour and make hour a col
        startHour = df['hour'].iloc[0]
        currentHour = (int(startHour) + hour)

        #Row to search for
        if currentHour < 10:
            currentHour = '0' + str(currentHour)

        #Find corresponding data with the hour point
        while True:
            num = df[df['hour'] == str(currentHour)].index
            #If match found then break
            if not num.empty:
                num = num[0]  # Get the index of the first matching row
                break  # Exit the loop if a match is found
            #Else than subtract one to find the last hour and don't move on the map
            else:
                currentHour = int(currentHour) - 1
                if currentHour < 10:
                    currentHour = '0' + str(currentHour)

        #This is the path that the plane takes
        path = df[['lat', 'lon']].values.tolist()

        # Iterate through the airport data and add markers to the map
        folium.PolyLine(path[:num + 1], popup=f'Departure Airport: {airport}', color='blue').add_to(m)

    return m

if __name__ == '__main__':
    app.run()
    
