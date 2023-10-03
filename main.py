import requests
import matplotlib.pyplot as plt

# Replace 'YOUR_API_KEY' with your AviationStack API key
API_KEY = '042753dc1ba431e8e1d24b8a2cb1d7e5'

# Flight ICAO24 identifier (replace with the desired flight's ICAO24)
ICAO24 = 'ABFE45'

# AviationStack API endpoint for flight tracking
API_ENDPOINT = f'http://api.aviationstack.com/v1/flights?access_key={API_KEY}&icao24={ICAO24}'

def get_flight_data():
    try:
        response = requests.get(API_ENDPOINT)
        data = response.json()
        return data['data'][0]  # Assuming we are interested in the first result
    except Exception as e:
        print(f"Error fetching flight data: {str(e)}")
        return None

def plot_flight_position(flight_data):
    if flight_data:
        latitude = flight_data['latitude']
        longitude = flight_data['longitude']

        plt.figure(figsize=(10, 6))
        plt.scatter(longitude, latitude, c='red', label='Flight Position')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Flight Tracking')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    flight_data = get_flight_data()
    if flight_data:
        print("Flight Data:")
        #print(f"Flight ICAO24: {flight_data['icao24']}")
        #print(f"Flight Callsign: {flight_data['callsign']}")
        #print(f"Latitude: {flight_data['latitude']}")
        #print(f"Longitude: {flight_data['longitude']}")
        print(flight_data)
        plot_flight_position(flight_data)
