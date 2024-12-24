from pydantic import BaseModel
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional
from calendar import monthrange

class Date(BaseModel):
    year: int = Field(..., ge=1, le=9999)
    month: Optional[int] = Field(None)
    day: Optional[int] = Field(None)

class Location(BaseModel):
    country: str
    region_id: int
    region: str
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

class TargetType(BaseModel):
    target_type_id: int
    target_type_name: str


class AttackType(BaseModel):
    attack_type_id: int
    attack_type_name: str


class Casualties(BaseModel):
    fatalities: Optional[float] = Field(None, ge=0)
    injuries: Optional[float] = Field(None, ge=0)



class WeaponType(BaseModel):
    weapon_type_id: int
    weapon_type_name: str


class TerroristGroup(BaseModel):
    group_name: str
    

class EventModel(Document,BaseModel):
    location: Location
    date: Date
    target_type: TargetType
    attack_type: AttackType
    number_of_terrorists: Optional[float] = Field(None, ge=0)
    casualties: Casualties
    summary: Optional[str]
    weapon_type: Optional[WeaponType]
    terrorist_group: Optional[TerroristGroup]

    class Settings:
      
        collection = "events"

    class Index:
        
        indexes = [
            ["date.year", "date.month", "date.day"], 
            ["location.country", "location.region"],  
            ["target_type.target_type_name"],  
            ["attack_type.attack_type_name"],  
            ["weapon_type.weapon_type_name"],  
        ]

