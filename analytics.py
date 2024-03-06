import pandas as pd

def getPrices(df, fleetDict):
    """
    Purpose:
        Return a list of prices for the flights total profit

    ARGS:
        df dataframe: This is the dataframe that the user chose to simulate
    """
    A321NEOList = []
    A330List = []
    B787List = []

    A321NEOdf = pd.DataFrame(columns=['Airport', 'FlightName', 'AllSeats', 'OccupiedSeats', 'TotalCost', 'ChargePerPassenger', 'TotalProfit', 'NetRevenue'])
    A330df = pd.DataFrame(['Airport', 'AllSeats', 'OccupiedSeats', 'CostPerFlight', 'ChargePerPassenger', 'TotalCost', 'TotalProfit'])
    B787df = pd.DataFrame(['Airport', 'AllSeats', 'OccupiedSeats', 'CostPerFlight', 'ChargePerPassenger', 'TotalCost', 'TotalProfit'])

    #totalPriceList = []

    # Get the Operating Cost Per ASM, and Operating Revenue Per ASM 2023
    # from https://newsroom.hawaiianairlines.com/releases/hawaiian-holdings-reports-2023-fourth-quarter-and-full-year-financial-results
    operatingRevenuePerASM = 0.1344
    operatingCostPerASM = 0.149

    # Get how many seats filled by multiplying num seats by factor
    Q1Load = .782
    Q2Load = .867
    Q3Load = .861
    Q4Load = .835

    #Get the total miles for the flight
    for airport,data in df.iterrows():
        print(airport)
        # Get the number of miles of the flight
        miles = df.loc[airport, 'miles']
        ICAO = df.loc[airport, 'ICAO']

        # Get the totalnumber of seats for each plane
        # seatNumA321NEO = df.loc[airport, 'numPlanesA321NEO'] * fleetDict['A321-Neo']['seats']
        # seatNumA330 = df.loc[airport, 'numPlanesA330'] * fleetDict['A330']['seats']
        # seatNumB787 = df.loc[airport, 'numPlanesB787'] * fleetDict['B787']['seats']

        # Add a new row for each flight
        for flight in range(df.loc[airport, 'numPlanesA321NEO']):

            # Assign total number of seats available
            allSeats = fleetDict['A321-Neo']['seats']

            #Assign flight name
            flightName = ICAO[1:] + str(flight+1)

            # Get the number of seats filled
            occupiedSeats = round(allSeats * Q2Load)

            # Get the total cost of the flight
            totalCost = int(miles) * operatingCostPerASM * int(allSeats)

            # Get the charge per passenger to break even
            chargePerPassenger = totalCost / occupiedSeats

            # Get the total profit for the flight
            totalProfit = chargePerPassenger * occupiedSeats

            # Get the net profit for the flight
            netRevenue = totalProfit - totalCost

            rowToAdd = {
                'Airport': airport,
                'FlightName': flightName,
                'AllSeats': allSeats,
                'OccupiedSeats': occupiedSeats,
                'TotalCost': "{:,.2f}".format(float(totalCost)),        # Format to 2 decimal places
                'ChargePerPassenger': "{:,.2f}".format(float(chargePerPassenger)),        # Format to 2 decimal places
                'TotalProfit': "{:,.2f}".format(float(totalProfit)),        # Format to 2 decimal places
                'NetRevenue': "{:,.2f}".format(float(netRevenue))        # Format to 2 decimal places
            }

            A321NEOdf = A321NEOdf.append(rowToAdd, ignore_index=True)

        # #Get the price for the flight
        # priceA330 = miles * operatingCostPerASM * seatNumA330
        # priceB787 = miles * operatingCostPerASM * seatNumB787

        # priceA321NEO = miles * operatingCostPerASM * seatNumA321NEO
        # priceListA321NEO.append("{:.2f}".format(float(priceA321NEO)))

        # priceListA330.append("{:.2f}".format(float(priceA330)))
        # priceListB787.append("{:.2f}".format(float(priceB787)))
        # totalPriceList.append("{:.2f}".format(float(priceA321NEO + priceA330 + priceB787)))

    return A321NEOdf