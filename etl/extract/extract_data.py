import pandas as pd
from dotenv import load_dotenv
import os
from extract.validate_data import validate_events

load_dotenv()

CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

df = pd.read_csv(CSV_FILE_PATH, encoding='ISO-8859-1')
df['summary'] = df['summary'].fillna('Unknown') 

selected_columns = [
    "eventid", "iyear", "imonth", "iday",
    "country_txt", "region", "city", "latitude", "longitude",
    "attacktype1", "attacktype1_txt",
    "targtype1", "targtype1_txt",
    "weaptype1", "weaptype1_txt",
    "gname","nperps",
    "nkill", "nwound", "summary"
]

data = df[selected_columns].to_dict(orient='records')

validated_data = validate_events(data)
