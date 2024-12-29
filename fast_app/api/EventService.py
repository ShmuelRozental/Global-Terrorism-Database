import logging
import math
import pandas as pd
from typing import Dict, List, Optional, Tuple
import folium
from folium.plugins import HeatMap
from fast_app.api.utils.folium_utils import generate_map_with_markers
from .EventRepo import EventRepo
from .utils.region_cordinate import REGION_COORDINATES

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class EventService:
    def __init__(self, event_repo: EventRepo):
        self.event_repo = event_repo


    @staticmethod
    def create_popup_and_tooltip_template(fields: List[str]) -> Tuple[str, str]:
        def popup_template(event: dict) -> str:
            return "\n".join([f"{field}: {event.get(field, 'N/A')}" for field in fields if field in event])

        def tooltip_template(event: dict) -> str:
            return event.get(fields[0], 'Unknown') if fields else 'Unknown'

        return popup_template, tooltip_template

    #1
    async def get_most_deadly_attacks_types(self, top_n: int) -> List[dict]:
        return await self._fetch_top_entities(field="attack_type.attack_type_name", top_n=top_n)

    #2
    async def get_avg_casualties_by_region(self, top_n: int = None) -> folium.Map:
        top_events = await self._fetch_top_entities(field="location.region", top_n=top_n)

        fields = ['total_casualties', 'avg_casualties', 'num_events']
        popup_template, tooltip_template = self.create_popup_and_tooltip_template(fields)

        return generate_map_with_markers(
            events=top_events,
            default_coords=REGION_COORDINATES,
            popup_template=popup_template,
            tooltip_template=tooltip_template
        )
    

    #3
    async def get_top_events_by_gname(self, top_n: int) -> List[dict]:
        return await self._fetch_top_entities(field="terrorist_group.group_name", top_n=top_n)

    #1,2,3
    async def _fetch_top_entities(self, field: str, top_n: int = None) -> List[dict]:
        if top_n is not None and top_n <= 0:
            raise ValueError("`top_n` must be a positive integer")

        return await self.event_repo.fetch_top_entities_by_field(field, top_n)


    #4
    async def calculate_attack_target_correlation(self, top_n: int = 10) -> Dict[str, Dict[str, int]]:
        attack_target_data = await self.event_repo.fetch_attack_target_data(top_n)
        if not attack_target_data:
            print("No data fetched")
            return {}

        print("Fetched attack_target_data:", attack_target_data)

        
        data = pd.DataFrame(attack_target_data)


        data['attack_type'] = data['_id'].apply(lambda x: x['attack_type'] if isinstance(x, dict) else '')
        data['target_type'] = data['_id'].apply(lambda x: x['target_type'] if isinstance(x, dict) else '')
        data['count'] = data['count']

    
        data.drop(columns=['_id'], inplace=True)

        correlation_data = {}
        for _, row in data.iterrows():
            attack_type = row['attack_type']
            target_type = row['target_type']
            count = row['count']

            if attack_type not in correlation_data:
                correlation_data[attack_type] = {}
            correlation_data[attack_type][target_type] = count

        return correlation_data
    

    #5
    async def get_yearly_attack_frequency(self):
        data = await self.event_repo.fetch_event_data()
        df = pd.DataFrame(data)

        df['year'] = df['date'].apply(lambda d: d['year'])

        yearly_frequency = df.groupby('year')['_id'].nunique().reset_index()
        yearly_frequency.columns = ['Year', 'Frequency']
        return yearly_frequency.to_dict(orient='records') 
    #5
    async def get_monthly_attack_frequency(self, year):
        data = await self.event_repo.fetch_event_data()
        df = pd.DataFrame(data)

        df['year'] = df['date'].apply(lambda d: d['year'])
        df['month'] = df['date'].apply(lambda d: d['month'])
        df = df[df['year'] == year]

        monthly_frequency = df.groupby('month')['_id'].nunique().reset_index()
        monthly_frequency.columns = ['Month', 'Frequency']
        return monthly_frequency.to_dict(orient='records')
    


    #7
    async def get_heat_map_with_time(self, year: Optional[int] = None, month: Optional[int] = None) -> dict:
        events = await self.event_repo.fetch_heat_map_with_time(year, month)
  
        if year and month:
            events = [event for event in events if event['date']['year'] == year and event['date']['month'] == month]

        grouped_events = self.group_events_by_time(events)

        heat_map_data = {
            "monthly": [],
            "yearly": [],
            "three_years": [],
        }

        for category, events_list in grouped_events.items():
            for event in events_list:
                latitude = event[1] 
                longitude = event[2] 
                heat_map_data[category].append([latitude, longitude])
        
        return heat_map_data



    #7
    def group_events_by_time(self, events):
        events_by_time = {"monthly": [], "yearly": [], "three_years": []}
        for grouped_event in events:
            try:
                region = grouped_event["_id"]["region"]
                year = grouped_event["_id"]["year"]
                month = grouped_event["_id"]["month"]
                for event in grouped_event["events"]:
                    if "lat" in event and "lon" in event:
                        latitude = event["lat"]
                        longitude = event["lon"]
                        

                        month_key = f"{year}-{month:02d}"
                        events_by_time["monthly"].append((month_key, latitude, longitude))
                        

                        year_key = f"{year}"
                        events_by_time["yearly"].append((year_key, latitude, longitude))
                        
   
                        three_years_key = (year // 3) * 3
                        events_by_time["three_years"].append((three_years_key, latitude, longitude))
            except Exception as e:
                print(f"Error processing event: {grouped_event} | Error: {e}")
        
        print("Grouped events by time:")
        for key, group in events_by_time.items():
            print(f"{key}: {len(group)} events")
        return events_by_time

    #7
    def create_heat_map(self, heat_map_data):

        m = folium.Map(location=[52.50153, 13.401851], zoom_start=6)

        for category, locations in heat_map_data.items():

            valid_locations = [
                (lat, lon) for lat, lon in locations if not (math.isnan(lat) or math.isnan(lon))
            ]
            

            if valid_locations:
                HeatMap(valid_locations).add_to(m)

        return m._repr_html_()

    #11
    async def get_shared_targets_map(self, region: str = None, country: str = None, limit: int = 1) -> folium.Map:
        events = await self.event_repo.fetch_shared_target_events(region, country, limit)
        if not events:
            raise ValueError("No events found for the specified region or country.")

        popup_template = lambda event: (
            f"Area: {event['_id']}\n"
            f"Groups: {', '.join(event.get('groups', []))}\n"
            f"Shared Targets: {event.get('shared_targets')}"
        )
        tooltip_template = lambda event: f"Area: {event['_id']}"

        return generate_map_with_markers(
            events,
            REGION_COORDINATES,
            popup_template,
            tooltip_template
        )
    


    
    async def get_shared_attack_strategies(
        self, 
        region: Optional[str] = None, 
        country: Optional[str] = None, 
        limit: int = 10
    ) -> folium.Map:
        events = await self.event_repo.fetch_shared_attack_strategies(region, country, limit)
        print("Events:", events[1])
        if not events:
            raise ValueError("No events found for the specified region or country.")

        popup_template = lambda event: (
            f"Region: {event['_id'].split(' - ')[0]}\n"
            f"Attack Type: {event['_id'].split(' - ')[1]}\n"
            f"Unique Groups: {len(event.get('unique_groups', []))}\n"
            f"Total Attacks: {event.get('total_attacks')}"
        )

        tooltip_template = lambda event: f"Region: {event['_id']}"

        return generate_map_with_markers(
            events=events,
            default_coords=REGION_COORDINATES,  
            popup_template=popup_template,
            tooltip_template=tooltip_template,
            initial_zoom=2
        )