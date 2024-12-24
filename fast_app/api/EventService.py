from typing import List
import folium
from .repo import EventRepo
from .utils.region_cordinate import REGION_COORDINATES

class EventService:
    def __init__(self, event_repo: EventRepo):
        self.event_repo = event_repo



    async def get_top_events_map(self, top_n: int = None) -> folium.Map:
        top_events = await self.event_repo.fetch_avg_casualties_by_region(top_n)
        
        event_map = folium.Map(location=[0, 0], zoom_start=2)
        
        if top_n is None:
            for region, coords in REGION_COORDINATES.items():
                lat = coords['lat']
                lon = coords['lon']
                
                
                region_data = next((event for event in top_events if event['_id'] == region), None)
                
                if region_data:
                 
                    total_casualties = region_data['total_casualties']
                    avg_casualties = region_data['avg_casualties']
                    num_events = region_data['num_events']
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=(
                            f"{region}: {total_casualties} total casualties\n"
                            f"Average Casualties: {avg_casualties}\n"
                            f"Number of Events: {num_events}"
                        ),
                        tooltip=region
                    ).add_to(event_map)
                else:
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"{region}: basic location",
                        tooltip=region
                    ).add_to(event_map)
        else:

            for event in top_events:
                lat = event.get("lat")
                lon = event.get("lon")
                if lat and lon:
                    folium.Marker(
                        location=[lat, lon],
                        popup=(
                            f"{event['_id']}: {event['total_casualties']} total casualties\n"
                            f"Average Casualties: {event['avg_casualties']}\n"
                            f"Number of Events: {event['num_events']}"
                        ),
                        tooltip=event['_id']
                    ).add_to(event_map)

        return event_map
