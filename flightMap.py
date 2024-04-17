from folium import PolyLine
import pandas as pd
import folium 
import pymongo
import os

#Connect to mongo
databaseInfo = os.getenv("FLIGHT_MONGO_INFO")
client = pymongo.MongoClient(databaseInfo)

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
    colorArr = ['darkblue', 'red', 'darkgreen', 'orange', 'purple', 'lightblue', 'lightgreen']

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