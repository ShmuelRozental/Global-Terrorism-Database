from typing import List
from .models.event import EventModel
from .utils.utils import serialize_doc
from motor.motor_asyncio import AsyncIOMotorDatabase

class EventRepo:
    def __init__(self, db: AsyncIOMotorDatabase):  
        self.db = db

    async def fetch_top_events_by_casualties(self, top_n: int = 5) -> List[dict]:
        pipeline = [
            {
                "$group": {
                    "_id": "$attack_type.attack_type_name",
                    "total_casualties": {
                        "$sum": {"$add": [{"$multiply": ["$casualties.fatalities", 2]}, "$casualties.injuries"]}
                    }
                }
            },
            {"$sort": {"total_casualties": -1}},
            {"$limit": top_n}  
        ]
        events_cursor = self.db.events.aggregate(pipeline)
        events = await events_cursor.to_list(length=None)  
        return [serialize_doc(event) for event in events] 
    

    async def fetch_avg_casualties_by_region(self, top_n: int = 5) -> List[dict]:
        if top_n is None:
            top_n = 12
        pipeline = [
            {"$match": {"location.lat": {"$ne": None}, "location.lon": {"$ne": None}}},
        {
            "$group": {
                "_id": "$location.region",  
                "lat": {"$first": "$location.lat"}, 
                "lon": {"$first": "$location.lon"},  
                "avg_casualties": {
                    "$avg": {"$add": [{"$multiply": ["$casualties.fatalities", 2]}, "$casualties.injuries"]}
                },  
                "total_casualties": {
                    "$sum": {"$add": [{"$multiply": ["$casualties.fatalities", 2]}, "$casualties.injuries"]}
                },  
                "num_events": {"$sum": 1}  
            }
        },
        {"$sort": {"total_casualties": -1}},  
        {"$limit": top_n}  
    ]
        events_cursor = self.db.events.aggregate(pipeline)
        events = await events_cursor.to_list(length=None)
        return [serialize_doc(event) for event in events]
