import pandas as pd
df = pd.read_csv("./data/csv/match_log.csv", sep=';', usecols=['Path1', 'Path2'])
import pandas as pd

Path = 'https://api-gw.sovereignsolutions.com/gateway' + df['Path1'] + ';' + df['Path2']
# Path_OSRM = 'https://router.project-osrm.org/route/v1/driving/13.388860,52.517037;13.397634,52.529407;13.428555,52.523219?overview=false
Path_OSRM = 'https://router.project-osrm.org/match/v1/driving'
df['Path'] = Path


df.drop(columns=['Path1', 'Path2'], inplace=True)
pd.set_option('display.max_colwidth', None)

print(df.iloc[0])

