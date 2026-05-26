from fastapi import FastAPI
import uvicorn

from routes.employees import router

from database.connect import (
    Base,
    engine
)

from services.scheduler_service import (
    start_scheduler
)


app = FastAPI()

app.include_router(router)

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup_event():

    start_scheduler()


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3001,
        reload=True
    )