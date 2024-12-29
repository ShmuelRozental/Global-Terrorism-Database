from typing import Callable, List

import logging

logger = logging.getLogger("generate_map")
logging.basicConfig(level=logging.INFO)
import folium


def generate_map_with_markers(
    events: List[dict],
    default_coords: dict,
    popup_template: Callable[[dict], str],
    tooltip_template: Callable[[dict], str],
    initial_zoom: int = 2
) -> folium.Map:
    """
    Generate a folium map with markers for given events.

    :param events: List of events with necessary data.
    :param default_coords: Dictionary with coordinates for regions or locations.
    :param popup_template: Callable to generate popup text for each event.
    :param tooltip_template: Callable to generate tooltip text for each event.
    :param initial_zoom: Initial zoom level for the map.
    :return: Folium map with markers.
    """
    event_map = folium.Map(location=[0, 0], zoom_start=initial_zoom)
    for event in events:
        region = event.get("_id")
        region_name = region.split(' - ')[0]
        region_coords = default_coords.get(region_name)

        if not region_coords:
            logger.warning(f"Skipping event with missing coordinates for region: {region}")
            continue

        lat, lon = region_coords.get("lat"), region_coords.get("lon")
        if lat is None or lon is None:
            logger.warning(f"Skipping event with invalid coordinates: lat={lat}, lon={lon}")
            continue

        popup_text = popup_template(event)
        tooltip_text = tooltip_template(event)
        folium.Marker(location=[lat, lon], popup=popup_text, tooltip=tooltip_text).add_to(event_map)

    return event_map
