from pyopensky.impala import Impala
import matplotlib.pyplot as plt
from folium import PolyLine
import pandas as pd
import folium 
from folium import plugins
import webbrowser
from flask import Flask, render_template, redirect
import time
import json
import asyncio

# Create an instance of the Impala class with authentication credentials
opensky = Impala(
    username="MCallahan03",
    password="Soccer21!",
    host="data.opensky-network.org",
    port=2230  # The port for the Impala shell
)

app = Flask(__name__)

@app.route('/')
def show_map():
    return render_template('/index.html')

@app.route('/add_marker/0', methods=['GET'])
def show_map2():
    m = getFlightInfo("Honloulou", "Phoenix", 0)
    #redirect("/add_marker/100")
    return m._repr_html_()

@app.route('/add_marker/100', methods=['GET'])
def show_map3():
    m = getFlightInfo("Honloulou", "Phoenix", 100)
    return m._repr_html_()

def getFlightInfo(arrivalAirport, departureAirport, num):
    """Get the info for a flight that is incoming from one airport and exiting from another

    ARGS:
        arrivalAirport string: this is the city of where the airport is located where the plane arrives from
        departureAirport string: this is the city of where the airport is located where the plane leaves from
    """

    airportDict = {
    "Austin": {"ICAO": "KAUS", "latitude": 30.2025, "longitude": -97.6650},
    "Boston": {"ICAO": "KBOS", "latitude": 42.3641, "longitude": -71.0052},
    "Vegas": {"ICAO": "KLAS", "latitude": 36.0840, "longitude": -115.1536},
    "Long Beach": {"ICAO": "KLGB", "latitude": 33.8177, "longitude": -118.1516},
    "Los Angeles": {"ICAO": "KLAX", "latitude": 33.9416, "longitude": -118.4085},
    "New York City": {"ICAO": "JFK", "latitude": 40.6413, "longitude": -73.7781},
    "Oakland": {"ICAO": "KOAK", "latitude": 37.7214, "longitude": -122.2208},
    "Ontario": {"ICAO": "KONT", "latitude": 34.0551, "longitude": -117.6006},
    "Phoenix": {"ICAO": "KPHX", "latitude": 33.4342, "longitude": -112.0080},
    "Portland": {"ICAO": "KPDX", "latitude": 45.5898, "longitude": -122.5951},
    "Sacramento": {"ICAO": "KSMF", "latitude": 38.6957, "longitude": -121.5908},
    "San Diego": {"ICAO": "SAN", "latitude": 32.7336, "longitude": -117.1897},
    "San Francisco": {"ICAO": "SFO", "latitude": 37.7749, "longitude": -122.4194},
    "San Jose": {"ICAO": "KSJC", "latitude": 37.3541, "longitude": -121.9375},
    "Seattle": {"ICAO": "KSEA", "latitude": 47.4502, "longitude": -122.3088}
    }

    # Airbus test flights from and to Toulouse airport
    list = opensky.flightlist(
        start="2023-07-03 00:00",
        end="2023-07-03 12:00",
        #icao24="A19A21",
        departure_airport=airportDict[departureAirport]["ICAO"],
        arrival_airport="PHNL",
        callsign="HAL%",
        limit=1
    )

    hist = opensky.history(
    start="2023-07-03 03:00",
    end="2023-07-03 09:00",
    icao24=list.loc[0,"icao24"],
    callsign=list.loc[0,"callsign"]
    )

    df = pd.DataFrame(hist)
    df['lat'] = df['lat'].fillna(33.9416)
    df['lon'] = df['lon'].fillna(-118.4085)
    df[['lat','lon']]

    path = []
    
    path = df[['lat', 'lon']].values.tolist()

    m = folium.Map(location=[20, -160], zoom_start=4)
    folium.Marker(path[num], popup='Marker Popup Text').add_to(m)

    return m

if __name__ == '__main__':
    app.run()
    
