from pyopensky.impala import Impala
import matplotlib.pyplot as plt
from folium import PolyLine
import pandas as pd
import folium 
from folium import plugins
import pymongo
import json

# Create an instance of the Impala class with authentication credentials
opensky = Impala(
    username="MCallahan03",
    password="Soccer21!",
    host="data.opensky-network.org",
    port=2230  # The port for the Impala shell
)

def getFlightInfo(arrivalAirport, departureAirport):
    """Get the info for a flight that is incoming from one airport and exiting from another

    ARGS:
        arrivalAirport string: this is the city of where the airport is located where the plane arrives from
        departureAirport string: this is the city of where the airport is located where the plane leaves from
    """

    #Dictionary with all airports that Hawaiian Airlines flies to
    airportDict = {
    "Austin": {"ICAO": "KAUS", "latitude": 30.2025, "longitude": -97.6650},
    "Boston": {"ICAO": "KBOS", "latitude": 42.3641, "longitude": -71.0052},
    "Vegas": {"ICAO": "KLAS", "latitude": 36.0840, "longitude": -115.1536},
    "Long Beach": {"ICAO": "KLGB", "latitude": 33.8177, "longitude": -118.1516},
    "Los Angeles": {"ICAO": "KLAX", "latitude": 33.9416, "longitude": -118.4085},
    "New York City": {"ICAO": "KJFK", "latitude": 40.6413, "longitude": -73.7781},
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

    # Use the OpenSky API to Get the real life historical flight
    list = opensky.flightlist(
        start="2023-07-03 00:00",
        end="2023-07-03 12:00",
        #icao24="A19A21",
        departure_airport=airportDict[departureAirport]["ICAO"],
        arrival_airport="PHNL",
        callsign="HAL%",
        limit=1
    )

    # With that last query use the information to get the flight details
    hist = opensky.history(
    start="2023-07-03 03:00",
    end="2023-07-03 09:00",
    icao24=list.loc[0,"icao24"],
    callsign=list.loc[0,"callsign"]
    )

    #Make the dataframe of the information and all null values we can assume is at the airport
    df = pd.DataFrame(hist)
    df = df.reset_index(drop=True)
    df['lat'] = df['lat'].fillna(airportDict[departureAirport]["latitude"])
    df['lon'] = df['lon'].fillna(airportDict[departureAirport]["longitude"])
    
    #Format the time better to suit our data then put back to datetime
    df['time'] = df['time'].dt.strftime('%y-%m-%d %H')
    df['time'] = pd.to_datetime(df['time'])

    #Get starting day and make a day col
    df['day'] = df['time'].dt.strftime('%d')

    #Get starting and current hour and make hour a col
    df['hour'] = df['time'].dt.strftime('%H')

    return df

client = pymongo.MongoClient("mongodb+srv://michealcallahan24:apple@capstone.8yr2tov.mongodb.net/")
# Select the database
db = client["FlightPath"]

arrival = "Honolulu"
departure = "Seattle"

# Get flight data and select relevant columns
df = getFlightInfo(arrival, departure)
df = df[['icao24', 'callsign', 'lon', 'lat', 'hour', 'day']]

# Create a dictionary for the flight data
flight_data = {
    "arrival": arrival,
    "departure": departure,
    "icao24": df["icao24"].iloc[0],
    "callsign": df["callsign"].iloc[0],
    "points": []
}

# Iterate through the DataFrame and add each flight as a document in the "flights" array
for index, row in df.iterrows():
    location = {
        "lon": row["lon"],
        "lat": row["lat"],
        "hour": row["hour"],
        "day": row["day"]
        
    }
    flight_data["points"].append(location)

# Insert the flight_data into the MongoDB collection
db.Flights.insert_one(flight_data)
