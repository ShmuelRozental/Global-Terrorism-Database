from pydantic import ValidationError
from typing import List
from models.Event import EventModel, Location, Date, TargetType, AttackType, Casualties, TerroristGroup, WeaponType  

def extract_unique_mappings(data: List[dict], key_id: str, key_name: str):
    mapping = {}
    for row in data:
        if row.get(key_id) and row.get(key_name): 
            mapping[row[key_id]] = row[key_name]
    return mapping

def validate_events(data: List[dict]) -> List[EventModel]:
    validated_events = []

    target_types = extract_unique_mappings(data, "targtype1", "targtype1_txt")
    attack_types = extract_unique_mappings(data, "attacktype1", "attacktype1_txt")
    weapon_types = extract_unique_mappings(data, "weaptype1", "weaptype1_txt")
    terrorist_groups = extract_unique_mappings(data, "gname", "gname")

    for row in data:
        try:
            event = EventModel(
                event_id=row.get("eventid"),
                date=Date(
                    year=row.get("iyear"),
                    month=row.get("imonth"),
                    day=row.get("iday")
                ),
                location=Location(
                    country=row.get("country_txt"),
                    region_id=row.get("region"),
                    region=row.get("region_txt"),
                    city=row.get("city"),
                    lat=row.get("latitude"),
                    lon=row.get("longitude")
                ),
                target_type=TargetType(
                    target_type_id=row.get("targtype1"),
                    target_type_name=target_types.get(row.get("targtype1"))
                ),
                attack_type=AttackType(
                    attack_type_id=row.get("attacktype1"),
                    attack_type_name=attack_types.get(row.get("attacktype1"))
                ),
                number_of_terrorists=row.get("nperps"),
                casualties=Casualties(
                    fatalities=row.get("nkill", 0),
                    injuries=row.get("nwound", 0)
                ),
                summary=row.get("summary"),
                weapon_type=WeaponType(
                    weapon_type_id=row.get("weaptype1"),
                    weapon_type_name=weapon_types.get(row.get("weaptype1"))
                ) if row.get("weaptype1") else None,
                terrorist_group=TerroristGroup(
                    group_name=terrorist_groups.get(row.get("gname"))
                ) if row.get("gname") else None
            )
            validated_events.append(event.model_dump())
        except ValidationError as e:
            print(f"Validation error for row {row.get('eventid', 'Unknown')}: {e}")
    
    return validated_events
