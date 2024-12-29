import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse



from fast_app.api.utils.plot_utils import plot_attack_trends
from fast_app.api.utils.serialization_utils import convert_to_int
from .EventService import EventService
from .EventRepo import EventRepo
from .database.init_db import get_db


router = APIRouter()


def get_event_repo(db=Depends(get_db)):
    return EventRepo(db)


def get_event_service(event_repo: EventRepo = Depends(get_event_repo)):
    return EventService(event_repo)

#1
@router.get("/events/most_deadly_attacks_types", response_model=List[dict])
async def get_most_deadly_attacks_types(
    top_n: int = Query(5, description="Number of top events to fetch", gt=0),
    event_service: EventService = Depends(get_event_service)
):
    try:
        return await event_service.get_most_deadly_attacks_types(top_n=top_n)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

#2
@router.get("/events/avg_casualties_by_region", response_class=HTMLResponse)
async def get_avg_casualties_by_region(
    top_n: int = Query(0, ge=0, description="Number of top events to display on the map (0 for all)"),
    event_service: EventService = Depends(get_event_service)
):
    try:
        event_map = await event_service.get_avg_casualties_by_region(top_n if top_n > 0 else None)
        return event_map._repr_html_()
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<h1>Error</h1><p>{str(e)}</p>")

#3
@router.get("/events/top_events_by_gname", response_model=List[dict])
async def get_top_events_by_gname(
    top_n: int = Query(5, description="Number of top events to fetch"),
    event_service: EventService = Depends(get_event_service)
):
    try:
        return await event_service.get_top_events_by_gname(top_n=top_n)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    



#4
@router.get("/events/correlation_attack_target", response_class=HTMLResponse)
async def get_correlation_attack_target(
    top_n: int = Query(10, description="Number of top correlations to display"),
    event_service: EventService = Depends(get_event_service)
):
    try:
        correlation_data = await event_service.calculate_attack_target_correlation(top_n)

        html_content = "<h1>Attack Type to Target Type Correlation</h1>"
        html_content += "<table border='1'><tr><th>Attack Type</th><th>Target Type</th><th>Count</th></tr>"

        for attack_type, target_dict in correlation_data.items():
            for target_type, count in target_dict.items():
                html_content += f"<tr><td>{attack_type}</td><td>{target_type}</td><td>{count}</td></tr>"

        html_content += "</table>"

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<h1>Error</h1><p>{str(e)}</p>")
    


#5
@router.get("/events/trends")
async def get_trends(
    year: Optional[int] = Query(None, description="Year to generate monthly frequency"),
    plot: bool = Query(False, description="Whether to generate a graph"),
    event_service: EventService = Depends(get_event_service)
):
    try:
        if year and plot:
            data = await plot_attack_trends(event_service, year)
            return convert_to_int(data)
        
  
        elif year:
            monthly_trends = await event_service.get_monthly_attack_frequency(year)
            return {"monthly_trends": convert_to_int(monthly_trends)}
        

        elif plot:
            data = await plot_attack_trends(event_service, None)
            return convert_to_int(data)
   
        else:
            yearly_trends = await event_service.get_yearly_attack_frequency()
            return {"yearly_trends": convert_to_int(yearly_trends)}
    
    except Exception as e:
        return {"error": str(e)}
    



#7
@router.get("/events/heat_map_with_time", response_class=HTMLResponse)
async def get_heat_map_with_time(
    year: Optional[int] = Query(None, description="Year of the attacks"),
    month: Optional[int] = Query(None, description="Month of the attacks"),
    event_service: EventService = Depends(get_event_service)
):
    try:
        heat_map_data = await event_service.get_heat_map_with_time(year, month)
        map_html = event_service.create_heat_map(heat_map_data)
        return HTMLResponse(content=map_html)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    


#11
@router.get("/events/shared_targets", response_class=HTMLResponse)
async def get_groups_with_shared_targets(
    region: str = Query(None, description="Filter by region"),
    country: str = Query(None, description="Filter by country"),
    limit: int = Query(1, ge=1),
    event_service: EventService = Depends(get_event_service)
):
    try:
        map_data = await event_service.get_shared_targets_map(region, country, limit)
        return map_data._repr_html_()
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<h1>Error</h1><p>{str(e)}</p>")


@router.get("/shared_attack_strategies")
async def get_shared_attack_strategies(
    region: Optional[str] = None,
    country: Optional[str] = None,
    event_service: EventService = Depends(get_event_service)):
    try:
        map_ = await event_service.get_shared_attack_strategies(region, country)
        
        map_html = map_._repr_html_() 
        
        return HTMLResponse(content=map_html)
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<h1>Error</h1><p>{str(e)}</p>")