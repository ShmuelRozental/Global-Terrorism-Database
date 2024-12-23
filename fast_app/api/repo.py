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

        # Build the match conditions for city or region
        if area:
            match_conditions["$or"] = [
                {"location.city": area}, 
                {"location.region": area}  
            ]

        pipeline = [
            # Match stage
            {"$match": match_conditions},
            
            # Group stage: Add lat and lon to the results
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$ifNull": ["$location.city", False]}, 
                            "$location.city",  # Group by city
                            "$location.region"  # Fallback to group by region
                        ]
                    },
                    "lat": {"$first": "$location.lat"},  # Extract latitude
                    "lon": {"$first": "$location.lon"},  # Extract longitude
                    "avg_casualties": {
                        "$avg": {"$add": [{"$multiply": ["$casualties.fatalities", 2]}, "$casualties.injuries"]}
                    },
                    "num_events": {"$sum": 1}  # Count the number of events
                }
            },
            
            # Sort stage: Order by average casualties descending
            {"$sort": {"avg_casualties": -1}}
        ]
        
        # Execute the aggregation pipeline
        events_cursor = self.db.events.aggregate(pipeline)
        events = await events_cursor.to_list(length=None)
        
        # Serialize the documents
        return [serialize_doc(event) for event in events]