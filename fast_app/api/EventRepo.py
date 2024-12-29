from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from fast_app.api.models.event import EventModel
import logging

logger = logging.getLogger("uvicorn.error")
class EventRepo:

    CASUALTY_CALCULATION = {"$add": [{"$multiply": ["$casualties.fatalities", 2]}, "$casualties.injuries"]}
    
    VALID_FIELDS = [
        "location.region", 
        "attack_type.attack_type_name", 
        "terrorist_group.group_name"
    ]


    def __init__(self, db: AsyncIOMotorDatabase, default_top_n: int = 5):
        self.db = db
        self.default_top_n = default_top_n


    #1,2,3
    async def fetch_top_entities_by_field(self, field: str, top_n: int = None) -> List[dict]:
        if field not in self.VALID_FIELDS:
            raise ValueError(f"Invalid field '{field}'. Must be one of {self.VALID_FIELDS}")

        pipeline = [
            {"$group": {
                "_id": f"${field}",
                "total_casualties": {"$sum": self.CASUALTY_CALCULATION},
                "avg_casualties": {"$avg": self.CASUALTY_CALCULATION},
                "num_events": {"$sum": 1}
            }},
            {"$sort": {"total_casualties": -1}},
            {"$limit": top_n or 10}
        ]

        try:
            cursor = self.db.events.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error fetching top entities for field {field}: {e}")
            raise Exception("Database query failed")



    #4
    async def fetch_attack_target_data(self, top_n: int = 10) -> List[Dict[str, str]]:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "attack_type": "$attack_type.attack_type_name",
                        "target_type": "$target_type.target_type_name"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": top_n
            }
        ]
        cursor = self.db.events.aggregate(pipeline)
        results = await cursor.to_list(length=None)  
        return results
    

    #5
    async def fetch_event_data(self):
        pipeline = [
            {
                "$project": {
                    "date": 1,
                    "_id": 1
                }
            }
        ]
        return await self.db["events"].aggregate(pipeline).to_list(length=None)
    


    #7
    async def fetch_heat_map_with_time(self, year: Optional[int] = None, month: Optional[int] = None) -> List[dict]:
        pipeline = []

        pipeline.append({
            "$match": {
                "location.lat": {"$exists": True, "$ne": None, "$type": "double"},
                "location.lon": {"$exists": True, "$ne": None, "$type": "double"},
                "date.year": {"$exists": True, "$ne": None},
                "date.month": {"$exists": True, "$ne": None},
            }
        })


        if year:
            pipeline.append({"$match": {"date.year": year}})
        if month:
            pipeline.append({"$match": {"date.month": month}})

        pipeline.extend([
            {"$group": {
                "_id": {
                    "year": "$date.year",
                    "month": "$date.month",
                    "region": "$location.region",
                },
                "events": {"$push": {"lat": "$location.lat", "lon": "$location.lon", "date": "$date"}},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ])

        try:
            cursor = self.db.events.aggregate(pipeline)
            result = await cursor.to_list(length=None)

            return result
        except Exception as e:
            logger.error(f"Error fetching heat map data: {e}")
            raise


    #11
    async def fetch_shared_target_events(self, region: str = None, country: str = None, limit: int = 1) -> List[dict]:
        match_stage = {}
        if region:
            match_stage["location.region"] = region
        if country:
            match_stage["location.country"] = country

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {"$group": {
                "_id": "$location.region",
                "groups": {"$addToSet": "$terrorist_group.group_name"},
                "shared_targets": {"$sum": 1}
            }},
            {"$sort": {"shared_targets": -1}},
            {"$limit": limit}  
        ])

        try:
            logger.info(f"Fetching shared target events for region: {region}, country: {country}")
            cursor = self.db.events.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            if not results:
                logger.info("No shared target events found for the given region or country.")
            return results
        except Exception as e:
            logger.error(f"Error fetching shared target events for region: {region}, country: {country}. Error: {e}")
            raise


  
    async def fetch_shared_attack_strategies(self, region: Optional[str] = None, country: Optional[str] = None, limit: int = 10):
        query = {}
        if region:
            query['location.region'] = region
        if country:
            query['location.country'] = country

        pipeline = [
            {"$match": query},  
            {"$unwind": { "path": "$attack_type", "preserveNullAndEmptyArrays": True }},  
            {"$group": {
                "_id": {
                    "$concat": [
                        "$location.region", " - ",
                        {"$ifNull": ["$attack_type.attack_type_name", "Unknown"]}
                    ]
                },
                "unique_groups": {"$addToSet": "$terrorist_group.group_name"},
                "total_attacks": {"$sum": 1}
            }},
            {"$sort": {"total_attacks": -1}},  
            {"$limit": limit}
        ]
            
      
        events = await self.db.events.aggregate(pipeline).to_list(length=None)  # אין צורך להשתמש ב-limit כאן אם יש לך ב-pipeline
        return events