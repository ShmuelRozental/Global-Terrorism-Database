from calendar import monthrange
import math
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional


class Date(BaseModel):
    year: int = Field(..., ge=1, le=9999)
    month: Optional[int] = Field(None)
    day: Optional[int] = Field(None)

    @model_validator(mode="after")
    def validate_date(self):
        if self.day is not None and self.month is None:
            raise ValueError("Day cannot be specified without a valid month.")
        
        if self.month and self.day:
            _, max_days = monthrange(self.year, self.month)
            if self.day < 1 or self.day > max_days:
                self.day = None
        
        return self


class Location(BaseModel):
    country: str
    region_id: int
    region: str
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


    @field_validator('city', mode="before")
    def check_city(cls, value):
        if isinstance(value, float) and math.isnan(value):
            return None  
        return value

    @field_validator('lat')
    def validate_lat(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90.")
        return v

    @field_validator('lon', mode="before")
    def check_lon(cls, v):
        if isinstance(v, float):
            if v < -180 or v > 180:
                return None  
        return v

class TargetType(BaseModel):
    target_type_id: int
    target_type_name: str


class AttackType(BaseModel):
    attack_type_id: int
    attack_type_name: str


class Casualties(BaseModel):
    fatalities: Optional[float] = Field(None, ge=0)
    injuries: Optional[float] = Field(None, ge=0)
    
    @field_validator('fatalities', 'injuries', mode="before")
    def validate_numbers(cls, value: Optional[float]):
        if value is not None and (value != value):
            return None  

        return value


class WeaponType(BaseModel):
    weapon_type_id: int
    weapon_type_name: str


class TerroristGroup(BaseModel):
    group_name: str
    

class EventModel(BaseModel):
    location: Location
    date: Date
    target_type: TargetType
    attack_type: AttackType
    number_of_terrorists: Optional[float] = Field(None, ge=0)
    casualties: Casualties
    summary: Optional[str]
    weapon_type: Optional[WeaponType]
    terrorist_group: Optional[TerroristGroup]

    @field_validator('number_of_terrorists', mode="before")
    def check_number_of_terrorists(cls, value):
        if value is not None:
            if isinstance(value, float):
                if value < 0 or math.isnan(value):
                    return None  
        return value