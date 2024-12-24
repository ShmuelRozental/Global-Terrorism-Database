from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from api.EventService import EventService
from .repo import EventRepo
from .database.init_db import get_db

router = APIRouter()


def get_event_repo(db=Depends(get_db)):
    return EventRepo(db)

def get_event_service(event_repo: EventRepo = Depends(get_event_repo)):
    return EventService(event_repo)

@router.get("/events", response_model=List[dict])
async def get_top_events_by_casualties(top_n: int = 5, event_repo: EventRepo = Depends(get_event_repo)):
    try:
        events = await event_repo.fetch_top_events_by_casualties(top_n=top_n)
        return events
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.get("/events/top_events_map", response_class=HTMLResponse)
async def get_top_events_map(top_n: int = 0, event_service: EventService = Depends(get_event_service)):
    try:
        event_map = await event_service.get_top_events_map(top_n if top_n > 0 else None)
        return event_map._repr_html_()
    except Exception as e:
        return HTMLResponse(status_code=500, content=f"<h1>Error</h1><p>{str(e)}</p>")
