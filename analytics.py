import pandas as pd
import random

# Dictionary to store all the information about their fleet
fleetDict = {
    "A321NEO": {"seats": 189, "economySeats": 128, "extraComfortSeats": 44, "firstClassSeats": 16, "numberOfPlanes": 18},
    "A330": {"seats": 278, "economySeats": 200, "extraComfortSeats": 60, "firstClassSeats": 18, "numberOfPlanes": 24},
    "B787": {"seats": 300, "economySeats": 187, "extraComfortSeats": 79, "firstClassSeats": 34, "numberOfPlanes": 2},
    "B717": {"seats": 128, "economySeats": 128, "extraComfortSeats": 0, "firstClassSeats": 8, "numberOfPlanes": 120},
}

def getPreset(plane):
    """
    Purpose:
        Return the preset analytics for the plane
    
    ARGS:
        plane str: This is the plane that the user chose
    """
    
    # Read the JSON file into a DataFrame
    readString = "presetAnalytics" + plane + ".json"
    df = pd.read_json(readString)

    # Define popularity ranking of airports
    popularity_ranking = {
        "Austin": 0,
        "Boston": 0,
        "Vegas": 3,
        "Long Beach": 1,
        "Los Angeles": 4,
        "Oakland": 2,
        "Ontario": 1,
        "Phoenix": 3,
        "Portland": 2,
        "Sacramento": 2,
        "San Diego": 2,
        "San Francisco": 2,
        "San Jose": 1,
        "Seattle": 2,
        "New York City": 2
    }

    # Modify values while considering popularity ranking and adding randomness
    if plane == "A321Neo":
        dfString = "Airbus A321NEO"
    elif plane == "A330":
        dfString = "Airbus A330"
    elif plane == "B787":
        dfString = "Boeing 787"

    for entry in df[dfString]:
        airport_name = entry["Airport Name"]
        popularity = popularity_ranking.get(airport_name, 0)

        # Seats
        econSeats = int(entry["Economy Seats"])
        extraComfortSeats = int(entry["Extra Comfort Seats"])
        firstClassSeats = int(entry["First Class Seats"])
        totalOccupiedSeats = econSeats + extraComfortSeats + firstClassSeats
        totalAvailableSeats = int(entry["Seats Available"])

        # Define random factor range based on popularity level
        if popularity == 0:
            random_factor_price = random.uniform(0.9, 0.975)
            random_factor_seats = random.uniform(0.85, 0.95)
        elif popularity == 1:
            random_factor_price = random.uniform(0.925, 1.0)
            random_factor_seats = random.uniform(0.9, 1.0)
        elif popularity == 2:
            random_factor_price = random.uniform(0.95, 1.025)
            random_factor_seats = random.uniform(0.95, 1.05)
        elif popularity == 3:
            random_factor_price = random.uniform(0.975, 1.05)
            random_factor_seats = random.uniform(1.0, 1.1)
        else:
            random_factor_price = random.uniform(1.0, 1.075)
            random_factor_seats = random.uniform(1.05, 1.15)
        
        # Adjust seats available based on popularity with randomness
        seats = round((totalOccupiedSeats * random_factor_seats), 0)

        # if seats is less than occupied
        if seats < totalOccupiedSeats:
            difference = totalOccupiedSeats - seats

            # minus 30% of the difference from economy seats
            entry["Extra Comfort Seats"] = extraComfortSeats - round(difference * 0.3, 0)

            # minus 70% from economy seats
            entry["Economy Seats"] = econSeats - round(difference * 0.7, 0)
        # if seats is more than occupied
        elif seats > totalOccupiedSeats:
            difference = seats - totalOccupiedSeats

            # add 25% of the difference to first class seats
            entry["First Class Seats"] = firstClassSeats + round(difference * 0.25, 0)

            # add 75% to extra comfort seats
            entry["Extra Comfort Seats"] = extraComfortSeats + round(difference * 0.75, 0)

        # Adjust actual charge prices based on popularity with randomness
        entry["Actual Charge"] = round(entry["Charge to Break Even"] * (random_factor_price), 2)

        # add the type of plane to df
        entry["Plane"] = plane

    # Flatten the nested dictionaries into separate columns
    df_flat = pd.json_normalize(df[dfString])

    return df_flat


def assignSeats(occupiedSeats, economySeats, extraComfortSeats, firstClassSeats):
    """
    Purpose:
        Assign the number of seats filled in each class

    ARGS:
        occupiedSeats int: This is the number of seats filled
        economySeats int: This is the number of economy seats
        extraComfortSeats int: This is the number of extra comfort seats
        firstClassSeats int: This is the number of first class seats
    """
    if occupiedSeats > economySeats + extraComfortSeats:
        # If there are more passengers than the sum of economy and extra comfort seats
        #   then fill all economy and extra comfort seats and the rest are first class
        occupiedSeatsEcon = economySeats
        occupiedSeatsExtraComfort = extraComfortSeats
        occupiedSeatsFirstClass = occupiedSeats - economySeats - extraComfortSeats
    elif occupiedSeats > economySeats:
        # If there are more passengers than the economy seats
        #   then fill all economy seats and the rest are extra comfort
        occupiedSeatsEcon = economySeats
        occupiedSeatsExtraComfort = occupiedSeats - economySeats
        occupiedSeatsFirstClass = 0
    else:
        # If there are less passengers than the economy seats
        #   then fill all the seats with economy passengers
        occupiedSeatsEcon = occupiedSeats
        occupiedSeatsExtraComfort = 0
        occupiedSeatsFirstClass = 0

    return occupiedSeatsEcon, occupiedSeatsExtraComfort, occupiedSeatsFirstClass

def getPricesPreset(df, airportDict, CASM, extraComfortMult, firstClassMult):

    # through each row of df
    for index, row in df.iterrows():
        # get the number of miles of the flight
        miles = airportDict[row['Airport Name']]['miles']

        # get the number of seats for the plane
        economySeats = row['Economy Seats']
        extraComfortSeats = row['Extra Comfort Seats']
        firstClassSeats = row['First Class Seats']
        seatsAvailable = row['Seats Available']

        # get the charge
        charge = row['Actual Charge']

        # get the operating cost
        totalCost = int(miles) * CASM * int(seatsAvailable)

        # get the total profit for the flight
        econProfit = int(economySeats) * charge
        extraComfortProfit = int(extraComfortSeats) * charge * extraComfortMult
        firstClassProfit = int(firstClassSeats) * charge * firstClassMult

        totalProfit = econProfit + extraComfortProfit + firstClassProfit

        # get the net revenue for the flight
        netRevenue = totalProfit - totalCost

        # add the values to the dataframe
        df.at[index, 'Operating Cost'] = "{:,.2f}".format(float(totalCost))
        df.at[index, 'Total Profit'] = "{:,.2f}".format(float(totalProfit))
        df.at[index, 'Net Revenue'] = "{:,.2f}".format(float(netRevenue))

    return df

def getTotalsPreset(df):
    """
    Purpose:
        Return the total statistics for the flights to fill totalDf

    ARGS:
        df dataframe: This is the dataframe that the user chose to simulate
    """

    # get total flights by length of df
    totalFlights = len(df)

    # Get all seats total by summing all the seats available
    allSeatsTotal = df['Seats Available'].sum()

    # Get number of plane types of each plane type
    numPlanesA321NEO = len(df[df['Plane'] == 'A321Neo'])
    numPlanesA330 = len(df[df['Plane'] == 'A330'])
    numPlanesB787 = len(df[df['Plane'] == 'B787'])

    # Get the total number of seats in each class using fleetDict
    economySeatsTotal = fleetDict['A321NEO']['economySeats'] * numPlanesA321NEO + fleetDict['A330']['economySeats'] * numPlanesA330 + fleetDict['B787']['economySeats'] * numPlanesB787
    extraComfortSeatsTotal = fleetDict['A321NEO']['extraComfortSeats'] * numPlanesA321NEO + fleetDict['A330']['extraComfortSeats'] * numPlanesA330 + fleetDict['B787']['extraComfortSeats'] * numPlanesB787
    firstClassSeatsTotal = fleetDict['A321NEO']['firstClassSeats'] * numPlanesA321NEO + fleetDict['A330']['firstClassSeats'] * numPlanesA330 + fleetDict['B787']['firstClassSeats'] * numPlanesB787

    # Get the total number of seats in each class
    occupiedSeatsEconTotal = df['Economy Seats'].sum()
    occupiedSeatsExtraComfortTotal = df['Extra Comfort Seats'].sum()
    occupiedSeatsFirstClassTotal = df['First Class Seats'].sum()

    # get occupied total seats
    occupiedSeatsTotal = occupiedSeatsEconTotal + occupiedSeatsExtraComfortTotal + occupiedSeatsFirstClassTotal

    #make operating cost into floats
    df['Operating Cost'] = df['Operating Cost'].str.replace(',', '').astype(float)
    df['Total Profit'] = df['Total Profit'].str.replace(',', '').astype(float)

    # get total cost
    totalCost = df['Operating Cost'].sum()

    # get total profit
    totalProfit = df['Total Profit'].sum()

    rowToAdd = {
        'TotalFlights': totalFlights,
        'TotalSeats': allSeatsTotal,
        'TotalSeatsEcon': economySeatsTotal,
        'TotalSeatsExtraComfort': extraComfortSeatsTotal,
        'TotalSeatsFirstClass': firstClassSeatsTotal,
        'OccupiedSeats': occupiedSeatsTotal,
        'OccupiedSeatsEcon': occupiedSeatsEconTotal,
        'OccupiedSeatsExtraComfort': occupiedSeatsExtraComfortTotal,
        'OccupiedSeatsFirstClass': occupiedSeatsFirstClassTotal,
        'TotalCost': "{:,.2f}".format(float(totalCost)),        # Format to 2 decimal places
        'TotalProfit': "{:,.2f}".format(float(totalProfit)),        # Format to 2 decimal places
        'NetRevenue': "{:,.2f}".format(float(totalProfit - totalCost))        # Format to 2 decimal places
    }

    # Add the row to the dataframe
    totalDf = pd.DataFrame()
    totalDf = totalDf.append(rowToAdd, ignore_index=True)

    return totalDf

        


def getTotals(df, fleetDict, load_factor, CASM, extraComfortMult, firstClassMult):
    """
    Purpose:
        Return the total statistics for the flights to fill totalDf

    ARGS:
        df dataframe: This is the dataframe that the user chose to simulate
        fleetDict dict: This is the dictionary that contains the information about the fleet
        load_factor float: This is the load factor that the user chose
        CASM float: This is the cost per available seat mile that the user chose
        extraComfort float: This is the multiplier for the extra comfort seats
        firstClass float: This is the multiplier for the first class seats
    """

    totalDf = pd.DataFrame()
    #Make a list of the fleet
    fleet = ['A321NEO', 'A330', 'B787']

    # set all variables with += to 0
    totalFlights = 0
    allSeatsTotal = 0
    economySeatsTotal = 0
    extraComfortSeatsTotal = 0
    firstClassSeatsTotal = 0
    occupiedSeatsTotal = 0
    occupiedSeatsEconTotal = 0
    occupiedSeatsExtraComfortTotal = 0
    occupiedSeatsFirstClassTotal = 0
    totalCost = 0
    totalProfit = 0

    #Get the total miles for the flight
    for airport,data in df.iterrows():

        # Get the number of miles of the flight
        miles = df.loc[airport, 'miles']

        # Add a new row for each flight
        for plane in fleet:

            # Total flight counter
            totalFlights += df.loc[airport, f'numPlanes{plane}']

            for flight in range(df.loc[airport, f'numPlanes{plane}']):

                # Add to seat totals
                allSeatsTotal += fleetDict[plane]['seats']
                economySeatsTotal += fleetDict[plane]['economySeats']
                extraComfortSeatsTotal += fleetDict[plane]['extraComfortSeats']
                firstClassSeatsTotal += fleetDict[plane]['firstClassSeats']

                # Assign total number of seats available
                allSeats = fleetDict[plane]['seats']
                economySeats = fleetDict[plane]['economySeats']
                extraComfortSeats = fleetDict[plane]['extraComfortSeats']
                firstClassSeats = fleetDict[plane]['firstClassSeats']

                # Get the number of seats filled
                occupiedSeats = round(allSeats * load_factor)
                
                # Assign the number of seats filled in each class
                occupiedSeatsEcon, occupiedSeatsExtraComfort, occupiedSeatsFirstClass = assignSeats(occupiedSeats, economySeats, extraComfortSeats, firstClassSeats)

                # Add to seat totals
                occupiedSeatsTotal += occupiedSeats
                occupiedSeatsEconTotal += occupiedSeatsEcon
                occupiedSeatsExtraComfortTotal += occupiedSeatsExtraComfort
                occupiedSeatsFirstClassTotal += occupiedSeatsFirstClass

                # Get the total cost of the flight. totalCost is the sum of all flights
                totalCost += int(miles) * CASM * int(allSeats)
                totalCostOfFlight = int(miles) * CASM * int(allSeats)

                # Get the charge per passenger to break even
                chargeExtraComfort = extraComfortMult * occupiedSeatsExtraComfort
                chargeFirstClass = firstClassMult * occupiedSeatsFirstClass 

                # Get the charge per passenger to break even
                chargePerPassenger = totalCostOfFlight / (occupiedSeatsEcon + chargeExtraComfort + chargeFirstClass)

                # Get the total profit for the flight
                chargeEcon = chargePerPassenger * occupiedSeatsEcon
                chargeExtraComfort = chargePerPassenger * extraComfortMult * occupiedSeatsExtraComfort
                chargeFirstClass = chargePerPassenger * firstClassMult * occupiedSeatsFirstClass

                totalProfit += chargeEcon + chargeExtraComfort + chargeFirstClass

    rowToAdd = {
        'TotalFlights': totalFlights,
        'TotalSeats': allSeatsTotal,
        'TotalSeatsEcon': economySeatsTotal,
        'TotalSeatsExtraComfort': extraComfortSeatsTotal,
        'TotalSeatsFirstClass': firstClassSeatsTotal,
        'OccupiedSeats': occupiedSeatsTotal,
        'OccupiedSeatsEcon': occupiedSeatsEconTotal,
        'OccupiedSeatsExtraComfort': occupiedSeatsExtraComfortTotal,
        'OccupiedSeatsFirstClass': occupiedSeatsFirstClassTotal,
        'TotalCost': "{:,.2f}".format(float(totalCost)),        # Format to 2 decimal places
        'TotalProfit': "{:,.2f}".format(float(totalProfit))        # Format to 2 decimal places
    }

    # Add the row to the dataframe
    totalDf = totalDf.append(rowToAdd, ignore_index=True)

    return totalDf

def getPrices(df, fleetDict, load_factor, CASM, extraComfortMult, firstClassMult):
    """
    Purpose:
        Return a list of prices for the flights total profit
        https://newsroom.hawaiianairlines.com/releases/hawaiian-holdings-reports-2023-fourth-quarter-and-full-year-financial-results

    ARGS:
        df dataframe: This is the dataframe that the user chose to simulate
        fleetDict dict: This is the dictionary that contains the information about the fleet
        load_factor float: This is the load factor that the user chose
        CASM float: This is the cost per available seat mile that the user chose
        extraComfort float: This is the multiplier for the extra comfort seats
        firstClass float: This is the multiplier for the first class seats
    """

    A321NEOdf = pd.DataFrame()
    A330df = pd.DataFrame()
    B787df = pd.DataFrame()

    # Divide load and CASM by 100 to get the actual value
    load_factor = load_factor / 100
    CASM = CASM / 100

    #Make a list of the fleet
    fleet = ['A321NEO', 'A330', 'B787']

    #Get the total miles for the flight
    for airport,data in df.iterrows():
        # Get the number of miles of the flight
        miles = df.loc[airport, 'miles']
        ICAO = df.loc[airport, 'ICAO']

        # Add a new row for each flight
        for plane in fleet:

            # Get the number of seats for the plane
            economySeats = fleetDict[plane]['economySeats']
            extraComfortSeats = fleetDict[plane]['extraComfortSeats']
            firstClassSeats = fleetDict[plane]['firstClassSeats']

            for flight in range(df.loc[airport, f'numPlanes{plane}']):

                # Assign total number of seats available
                allSeats = fleetDict[plane]['seats']

                #Assign flight name
                flightName = ICAO[1:] + str(flight+1)

                # Get the number of seats filled
                occupiedSeats = round(allSeats * load_factor)
                
                # Assign the number of seats filled in each class
                occupiedSeatsEcon, occupiedSeatsExtraComfort, occupiedSeatsFirstClass = assignSeats(occupiedSeats, economySeats, extraComfortSeats, firstClassSeats)

                # Get the total cost of the flight
                totalCost = int(miles) * CASM * int(allSeats)

                # Get the charge per passenger to break even
                chargeExtraComfort = extraComfortMult * occupiedSeatsExtraComfort
                chargeFirstClass = firstClassMult * occupiedSeatsFirstClass 

                chargePerPassenger = totalCost / (occupiedSeatsEcon + chargeExtraComfort + chargeFirstClass)

                # Get the total profit for the flight
                chargeEcon = chargePerPassenger * occupiedSeatsEcon
                chargeExtraComfort = chargePerPassenger * extraComfortMult * occupiedSeatsExtraComfort
                chargeFirstClass = chargePerPassenger * firstClassMult * occupiedSeatsFirstClass

                totalProfit = chargeEcon + chargeExtraComfort + chargeFirstClass

                # Get the net profit for the flight
                netRevenue = totalProfit - totalCost

                rowToAdd = {
                    'Airport': airport,
                    'FlightName': flightName,
                    'AllSeats': allSeats,
                    'OccupiedSeats': occupiedSeats,
                    'OccupiedSeatsEcon': occupiedSeatsEcon,
                    'OccupiedSeatsExtraComfort': occupiedSeatsExtraComfort,
                    'OccupiedSeatsFirstClass': occupiedSeatsFirstClass,
                    'TotalCost': "{:,.2f}".format(float(totalCost)),        # Format to 2 decimal places
                    'ChargePerPassenger': "{:,.2f}".format(float(chargePerPassenger)),        # Format to 2 decimal places
                    'TotalProfit': "{:,.2f}".format(float(totalProfit)),        # Format to 2 decimal places
                    'NetRevenue': "{:,.2f}".format(float(netRevenue))        # Format to 2 decimal places
                }

                #Add to the dataframe of the corresponding plane
                if plane == 'A321NEO':
                    A321NEOdf = A321NEOdf.append(rowToAdd, ignore_index=True)
                elif plane == 'A330':
                    A330df = A330df.append(rowToAdd, ignore_index=True)
                elif plane == 'B787':
                    B787df = B787df.append(rowToAdd, ignore_index=True)


    return A321NEOdf, A330df, B787df, getTotals(df, fleetDict, load_factor, CASM, extraComfortMult, firstClassMult)