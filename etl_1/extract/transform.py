import pandas as pd
from pydantic import ValidationError
from typing import List
from datetime import datetime
from model import Date, Location, TargetType, AttackType, Casualties, WeaponType, TerroristGroup, EventModel
from data.utils.country_region_map import country_region_map

def extract_unique_mappings(data: List[dict], key_name: str):
    mapping = {}
    for row in data:
        if row.get(key_name):
            mapping[row[key_name]] = row[key_name]
    return mapping

def transform_data(df: pd.DataFrame) -> pd.DataFrame:

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
    

    df['Date'] = df['Date'].apply(
        lambda x: x.replace(year=1900 + x.year % 100) if pd.notnull(x) and x.year > datetime.now().year else x
    )

    df['iyear'] = df['Date'].dt.year
    df['imonth'] = df['Date'].dt.month
    df['iday'] = df['Date'].dt.day

    return df

def transform_events(data: List[dict]) -> List[dict]:
    transformed_data = []

    target_types = extract_unique_mappings(data, "targtype1_txt")
    attack_types = extract_unique_mappings(data, "attacktype1_txt")
    weapon_types = extract_unique_mappings(data, "weaptype1_txt")
    terrorist_groups = extract_unique_mappings(data, "gname")
    
    for record in data:
        try:
            try:
                date_obj = Date.from_string(record['Date']) 
                record['date'] = date_obj
            except ValueError as e:
                print(f"Skipping record due to invalid date: {record['Date']}")
                continue

            country = record.get('country_txt', '')
            region = country_region_map.get(country, 'Unknown')

            location = Location(
                country=record.get('country_txt', ''),
                region_id=record.get('region_id', 0),
                region=region,
                city=record.get('city', ''),
                lat=record.get('latitude', None),
                lon=record.get('longitude', None)
            )
            record['location'] = location

            attack_type = AttackType(
                attack_type_id=record.get('attacktype1', None),
                attack_type_name=record.get('attacktype1_txt', '')
            )
            record['attack_type'] = attack_type

            target_type = TargetType(
                target_type_id=record.get('targtype1', None),
                target_type_name=record.get('targtype1_txt', '')
            )
            record['target_type'] = target_type

            casualties = Casualties(
                fatalities=record.get('nkill', 0),
                injuries=record.get('nwound', 0)
            )
            record['casualties'] = casualties

            weapon_type = WeaponType(
                weapon_type_id=record.get('weapon_type', None),
                weapon_type_name=record.get('Weapon', '')
            )
            record['weapon_type'] = weapon_type

            terrorist_group = TerroristGroup(
                group_name=record.get('gname', '')
            )
            record['terrorist_group'] = terrorist_group

            event = EventModel(
                location=record['location'],
                date=record['date'],
                target_type=record['target_type'],
                attack_type=record['attack_type'],
                casualties=record['casualties'],
                weapon_type=record['weapon_type'],
                terrorist_group=record['terrorist_group'],
                number_of_terrorists=record.get('number_of_terrorists', None),
                summary=record.get('summary', None)
            )

            # Add the serialized dictionary to the transformed_data
            transformed_data.append(event.model_dump())
        
        except ValidationError as e:
            print(f"Skipping record due to validation error: {e}")
        except ValueError as e:
            print(f"Skipping record due to invalid date: {record.get('Date')}")
            continue

    return transformed_data
