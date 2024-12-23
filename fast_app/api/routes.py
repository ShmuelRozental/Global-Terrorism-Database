from fastapi import APIRouter, Depends
from .repo import EventRepo
from .database.init_db import get_db

router = APIRouter()

def get_event_repo(db=Depends(get_db)):
    return EventRepo(db)  

@router.get("/events")
async def get_events(event_repo: EventRepo = Depends(get_event_repo)):
    events = await event_repo.get_events()  
    return {"data": events}

@router.get("/test_db")
async def test_db(db=Depends(get_db)):
    return {"status": "MongoDB connection successful!"}
