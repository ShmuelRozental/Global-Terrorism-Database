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

    async def fetch_avg_casualties_by_area(self, area: str = None) -> List[dict]:
        match_conditions = {}
        if area:
            match_conditions['area'] = area

        pipeline = [
            {"$match": match_conditions},


            {
                "$addFields": {
                    "score": {
                        "$add": [
                            {"$multiply": ["$casualties.injuries", 1]},  
                            {"$multiply": ["$casualties.fatalities", 2]} 
                        ]
                    }
                }
            },
            

            {
                "$group": {
                    "_id": "$area",
                    "total_casualties": {
                        "$sum": "$score"
                    },
                    "event_count": {
                        "$sum": 1 
                    }
                }
            },


            {
                "$addFields": {
                    "avg_casualties_per_event": {
                        "$divide": ["$total_casualties", "$event_count"]
                    }
                }
            },

            {"$sort": {"avg_casualties_per_event": -1}}
        ]

        events_cursor = self.db.events.aggregate(pipeline)
        events = await events_cursor.to_list(length=None)

        return [serialize_doc(event) for event in events]
