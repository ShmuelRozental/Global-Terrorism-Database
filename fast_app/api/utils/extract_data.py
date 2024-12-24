import csv
from database.init_db import get_db
from models.event import Event

def load_data(csv_file_path: str):
    db = get_db()
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        events = [Event(**row) for row in reader]
        db.events.insert_many([event.dict() for event in events])

if __name__ == "__main__":
    load_data('../data/globalterrorismdb_0718dist.csv')
