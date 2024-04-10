import pandas as pd

# Dictionary to store all the information about their fleet
fleetDict = {
    "A321NEO": {"seats": 189, "economySeats": 128, "extraComfortSeats": 44, "firstClassSeats": 16, "numberOfPlanes": 18},
    "A330": {"seats": 278, "economySeats": 200, "extraComfortSeats": 60, "firstClassSeats": 18, "numberOfPlanes": 24},
    "B787": {"seats": 300, "economySeats": 187, "extraComfortSeats": 79, "firstClassSeats": 34, "numberOfPlanes": 2},
    "B717": {"seats": 128, "economySeats": 128, "extraComfortSeats": 0, "firstClassSeats": 8, "numberOfPlanes": 120},
}

def getPrices(df, fleetDict, load_factor, CASM):
    """
    Purpose:
        Return a list of prices for the flights total profit
        https://newsroom.hawaiianairlines.com/releases/hawaiian-holdings-reports-2023-fourth-quarter-and-full-year-financial-results

    ARGS:
        df dataframe: This is the dataframe that the user chose to simulate
        fleetDict dict: This is the dictionary that contains the information about the fleet
        load_factor float: This is the load factor that the user chose
        CASM float: This is the cost per available seat mile that the user chose
    """

    A321NEOdf = pd.DataFrame(columns=['Airport', 'FlightName', 'AllSeats', 'OccupiedSeatsEcon', 'OccupiedSeatsExtraComfort', 'OccupiedSeatsFirstClass', 'TotalCost', 'ChargePerPassenger', 'TotalProfit', 'NetRevenue'])
    A330df = pd.DataFrame(columns=['Airport', 'FlightName', 'AllSeats', 'OccupiedSeatsEcon', 'OccupiedSeatsExtraComfort', 'OccupiedSeatsFirstClass', 'TotalCost', 'ChargePerPassenger', 'TotalProfit', 'NetRevenue'])
    B787df = pd.DataFrame(columns=['Airport', 'FlightName', 'AllSeats', 'OccupiedSeatsEcon', 'OccupiedSeatsExtraComfort', 'OccupiedSeatsFirstClass', 'TotalCost', 'ChargePerPassenger', 'TotalProfit', 'NetRevenue'])
    
    # Divide load and CASM by 100 to get the actual value
    load_factor = load_factor / 100
    CASM = CASM / 100

    #Make a list of the fleet
    fleet = ['A321NEO', 'A330', 'B787']

    #Get the total miles for the flight
    for airport,data in df.iterrows():
        print(airport)
        # Get the number of miles of the flight
        miles = df.loc[airport, 'miles']
        ICAO = df.loc[airport, 'ICAO']

        # Add a new row for each flight
        for plane in fleet:

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

                # Get the total cost of the flight
                totalCost = int(miles) * CASM * int(allSeats)

                # Get the charge per passenger to break even
                chargePerPassenger = totalCost / (occupiedSeatsEcon + 1.5 * occupiedSeatsExtraComfort + 3 * occupiedSeatsFirstClass)

                # Get the total profit for the flight
                totalProfit = chargePerPassenger * occupiedSeatsEcon + chargePerPassenger * 1.5 * occupiedSeatsExtraComfort + chargePerPassenger * 3 * occupiedSeatsFirstClass

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


    return A321NEOdf, A330df, B787df