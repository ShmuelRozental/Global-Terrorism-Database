from calendar import monthrange
from datetime import datetime
import math
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional





class Date(BaseModel):
    year: int = Field(..., ge=1, le=9999)
    month: Optional[int] = Field(None)
    day: Optional[int] = Field(None)

    @classmethod
    def from_string(cls, date_str: str) -> 'Date':
        try:
            dt = datetime.strptime(date_str, "%d-%b-%y")
            return cls(year=dt.year, month=dt.month, day=dt.day)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

    # @model_validator(mode="after")
    # def validate_date(cls, values):
    #     if values.get('day') is not None and values.get('month') is None:
    #         raise ValueError("Day cannot be specified without a valid month.")
        
    #     if values.get('month') and values.get('day'):
    #         _, max_days = monthrange(values['year'], values['month'])
    #         if values['day'] < 1 or values['day'] > max_days:
    #             raise ValueError(f"Invalid day {values['day']} for the month {values['month']} in the year {values['year']}.")
        
 
    #     if values.get('year') > datetime.now().year:
    #         values['year'] = 1900 + values['year'] % 100

    #     return values





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


class TargetType(BaseModel):
    target_type_id: Optional[int] = Field(None, ge=0)
    target_type_name: str


class AttackType(BaseModel):
    attack_type_id:  Optional[int] = Field(None, ge=0)
    attack_type_name: str


class Casualties(BaseModel):
    fatalities: Optional[float] = Field(None, ge=0)
    injuries: Optional[float] = Field(None, ge=0)

class WeaponType(BaseModel):
    weapon_type_id:  Optional[int] = Field(None, ge=0)
    weapon_type_name: str

    @field_validator('weapon_type_name', mode="before")
    def check_weapon_type_name(cls, value):
        if isinstance(value, float) and math.isnan(value):
            return ''  
        return value


class TerroristGroup(BaseModel):
    group_name: str

    @field_validator('group_name', mode="before")
    def check_group_name(cls, value):
        if isinstance(value, float) and math.isnan(value):
            return ''  
        return value



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