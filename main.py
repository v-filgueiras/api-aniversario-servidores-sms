from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes.api import router
from database.connect import Base, engine
from services.scheduler_service import start_scheduler

app = FastAPI()

app.include_router(router)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

Base.metadata.create_all(bind=engine)


@app.get("/")
def serve_admin_page():
    return FileResponse("frontend/index.html")


@app.on_event("startup")
async def startup_event():

    start_scheduler()

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3001
    )
