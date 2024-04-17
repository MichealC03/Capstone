function updateTotalValueTable(oldProfit, newProfit) {
    /*
    Purpose:
    This function updates the percentages of seats filled in the total table.
    It also increases the total operation cost, and profit. Then net revenue updates based on that

    ARGS:
    oldProfit: The old profit value
    newProfit: The new profit value
    */

    // Get the int values from the hidden inputs
    var occupiedSeats = parseInt(document.getElementById('OccupiedSeats').value);
    var totalSeats = parseInt(document.getElementById('TotalSeats').value);
    var occupiedSeatsEcon = parseInt(document.getElementById('OccupiedSeatsEcon').value);
    var totalSeatsEcon = parseInt(document.getElementById('TotalSeatsEcon').value);
    var occupiedSeatsExtraComfort = parseInt(document.getElementById('OccupiedSeatsExtraComfort').value);
    var totalSeatsExtraComfort = parseInt(document.getElementById('TotalSeatsExtraComfort').value);
    var occupiedSeatsFirstClass = parseInt(document.getElementById('OccupiedSeatsFirstClass').value);
    var totalSeatsFirstClass = parseInt(document.getElementById('TotalSeatsFirstClass').value);

    // Calculate the percentages of seats filled
    var percentSeats = (occupiedSeats / totalSeats) * 100;
    var percentSeatsEcon = (occupiedSeatsEcon / totalSeatsEcon) * 100;
    var percentSeatsExtraComfort = (occupiedSeatsExtraComfort / totalSeatsExtraComfort) * 100;
    var percentSeatsFirstClass = (occupiedSeatsFirstClass / totalSeatsFirstClass) * 100;

    // Update the values of percentages in the table. Format to 2 decimal places and a %
    document.getElementById('AllSeatsPercentage').textContent = percentSeats.toFixed(2) + '%';
    document.getElementById('EconPercentage').textContent = percentSeatsEcon.toFixed(2) + '%';
    document.getElementById('ExtraComfortPercentage').textContent = percentSeatsExtraComfort.toFixed(2) + '%';
    document.getElementById('FirstClassPercentage').textContent = percentSeatsFirstClass.toFixed(2) + '%';

    // Update the total profit and net revenue
    var totalProfit = parseFloat(document.getElementById('TotalProfit').textContent.replace(/,/g, ''));
    var newTotalProfit = totalProfit + newProfit - oldProfit;

    var totalCost = parseFloat(document.getElementById('TotalCost').textContent.replace(/,/g, ''));

    var netRevenue = newTotalProfit - totalCost;

    // Update the values in the table
    document.getElementById('TotalProfit').textContent = newTotalProfit.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    document.getElementById('TotalNetRevenue').textContent = netRevenue.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updateNewTotal(input, aircraftType) {
    /*
    Purpose:
    This function calculates the new total profit and net revenue based on the new charge per passenger.

    ARGS:
    parentRow: The parent row of the input element
    chargePerPassenger: The new charge per passenger
    totalCost: The total cost of the flight
    aircraftType: The type of aircraft that the user is changing the input for
    occupiedSeatsEcon: The number of occupied economy seats
    occupiedSeatsExtraComfort: The number of occupied extra comfort seats
    occupiedSeatsFirstClass: The number of occupied first class seats
    */

    // Get the parent row of the input element
    var parentRow = input.closest('tr');

    // create selectors with the aircraft type
    var totalSelector = `#${aircraftType}Total`;
    var econSelector = `#${aircraftType}Econ input`;
    var extraSelector = `#${aircraftType}Extra input`;
    var firstSelector = `#${aircraftType}First input`;
    var chargeSelector = `#${aircraftType}Actual input`;

    // Get the total cost and the occupied seats
    var totalCost = parentRow.querySelector(totalSelector).textContent.replace(/,/g, '');
    var occupiedSeatsEcon = parentRow.querySelector(econSelector).value;
    var occupiedSeatsExtraComfort = parentRow.querySelector(extraSelector).value;
    var occupiedSeatsFirstClass = parentRow.querySelector(firstSelector).value;
    var chargePerPassenger = parseFloat(parentRow.querySelector(chargeSelector).value);

    // Get the extra comfort and first class multipliers
    var extraComfortMult = parseFloat(document.getElementById('extraComfortMult').value);
    var firstClassMult = parseFloat(document.getElementById('firstClassMult').value);

    // Calculate the new total profit
    var econProfit = chargePerPassenger * occupiedSeatsEcon;
    var extraProfit = chargePerPassenger * extraComfortMult * occupiedSeatsExtraComfort;
    var firstProfit = chargePerPassenger * firstClassMult * occupiedSeatsFirstClass;

    var totalProfit = econProfit + extraProfit + firstProfit;

    // Calculate the new net revenue
    var netRevenue = totalProfit - totalCost;

    // Update the values in the table
    var totalProfitSelector = `#${aircraftType}TotalProfit`;
    var netRevenueSelector = `#${aircraftType}Revenue`;

    // Get the cells to update
    var totalProfitCell = parentRow.querySelector(totalProfitSelector);
    var netRevenueCell = parentRow.querySelector(netRevenueSelector);

    //Round to 2 decimal places
    totalProfit = totalProfit.toFixed(2);
    netRevenue = netRevenue.toFixed(2);

    // Update the values in the total table using the old profit and new profit
    var oldTotalProfit = parseFloat(parentRow.querySelector(totalProfitSelector).textContent.replace(/,/g, ''));
    updateTotalValueTable(oldTotalProfit, parseFloat(totalProfit));

    // Format the numbers with commas
    totalProfit = totalProfit.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    netRevenue = netRevenue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    // Update the values in the table
    totalProfitCell.textContent = totalProfit;
    netRevenueCell.textContent = netRevenue;
}

function changePrice(input, aircraftType) {
    /*
    Purpose:
    This function is called when the user changes the price of the ticket.

    ARGS:
    input: The input element that the user changed
    aircraftType: The type of aircraft that the user is changing the input for
    */

    // Calculate the new total profit and net revenue
    updateNewTotal(input, aircraftType);
}


function handleInputChange(input, aircraftType) {
    /*
    Purpose:
    This function is called when the user changes the number of occupied seats in the input field.

    ARGS:
    input: The input element that the user changed
    aircraftType: The type of aircraft that the user is changing the input for
    */

    // Get the parent row of the input element
    var parentRow = input.closest('tr');

    // create selectors with the aircraft type
    var totalSelector = `#${aircraftType}Total`;
    var econSelector = `#${aircraftType}Econ input`;
    var extraSelector = `#${aircraftType}Extra input`;
    var firstSelector = `#${aircraftType}First input`;

    // Get the total cost and the occupied seats
    var totalCost = parentRow.querySelector(totalSelector).textContent.replace(/,/g, '');
    var occupiedSeatsEcon = parentRow.querySelector(econSelector);
    var occupiedSeatsExtraComfort = parentRow.querySelector(extraSelector);
    var occupiedSeatsFirstClass = parentRow.querySelector(firstSelector);

    // Update the values of the occupied seats
    occupiedSeatsEcon = occupiedSeatsEcon.value;

    // Get the extra comfort and first class multipliers
    var extraComfortMult = parseFloat(document.getElementById('extraComfortMult').value);
    var firstClassMult = parseFloat(document.getElementById('firstClassMult').value);

    // Calculate the new number of occupied seats
    occupiedSeatsExtraComfort = extraComfortMult * occupiedSeatsExtraComfort.value;
    occupiedSeatsFirstClass = firstClassMult * occupiedSeatsFirstClass.value;

    // Calculate the new charge per passenger
    var sum = parseFloat(occupiedSeatsEcon) + parseFloat(occupiedSeatsExtraComfort) + parseFloat(occupiedSeatsFirstClass);
    var newValue = parseFloat(totalCost) / sum;
    
    // Round the value to 2 decimal places
    newValue = newValue.toFixed(2);

    // Update the value in the table
    var chargeSelector = `#${aircraftType}Charge`;
    var chargePerPassengerCell = parentRow.querySelector(chargeSelector);
    chargePerPassengerCell.textContent = newValue;

    // Calculate the new total profit and net revenue
    updateNewTotal(input, aircraftType);
}