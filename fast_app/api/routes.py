from fastapi import APIRouter
from api.database.init_db import get_db
from api.utils.utils import serialize_doc
from api.models.event import Event

router = APIRouter()

@router.get("/events")
async def get_events():
    db = get_db()
    events = db.events.find()
    return [serialize_doc(event) for event in events]
