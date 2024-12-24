import pandas as pd
from dotenv import load_dotenv
import os

from data.utils.rename_columns import rename_columns
from extract.transform import transform_events


load_dotenv()

CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

df = pd.read_csv(CSV_FILE_PATH, encoding='ISO-8859-1')



rename_columns(df)
data = df.to_dict(orient='records')
transformed_data = transform_events(data)
