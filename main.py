from pyopensky.impala import Impala
import pandas as pd

# Create an instance of the Impala class with authentication credentials
impala_instance = Impala(
    username="a",
    password="Soccer21!",
    host="data.opensky-network.org",
    port=2230  # The port for the Impala shell
)

hist = impala_instance.history(
    "2017-02-05 15:45",
    stop="2017-02-05 16:45",
    callsign="EZY158T",
    # returns a Flight instead of a Traffic
    return_flight=True
)

df = pd.DataFrame(hist)

print(df.lat)