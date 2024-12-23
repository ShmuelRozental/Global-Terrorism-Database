from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse

from fast_app.api.database.init_db import lifespan
from .routes import router
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)



app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



