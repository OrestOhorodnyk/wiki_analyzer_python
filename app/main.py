import asyncio
import logging
from app.constants import USER_CONTRIBUTES_REQUIRED_FIELDS
import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.api import router
from app.db import models
from app.db.database import SessionLocal, engine
from app.logger.costum_logging import CustomizeLogger
from datetime import datetime
from app.stream.recent_changes import get_stream

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title='Master App log', debug=False)
    logger = CustomizeLogger.make_logger()
    app.logger = logger
    app.include_router(router)
    return app


models.Base.metadata.create_all(bind=engine)
app = create_app()


async def random_n():
    for i in range(100000):
        print(i)
        await asyncio.sleep(5)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_user():
    db = SessionLocal()
    events = get_stream("https://stream.wikimedia.org/v2/stream/recentchange")
    async for event in events:
        try:
            msg = 'User: {user} \nEdited article: {title} \n\n'.format(**event)
            logger.debug(msg)
            uc = {field: event.get(field) for field in USER_CONTRIBUTES_REQUIRED_FIELDS}
            uc["timestamp"] = datetime.fromtimestamp(uc["timestamp"])
            user_contributes = models.UserContributes(**uc)
            db.add(user_contributes)
            db.commit()
        except Exception as err:
            logger.error(f"error {err}")
            logger.error(f"event:  {event}")
            break


@app.on_event("startup")
async def startup_event():
    create_user()
    task = asyncio.create_task(create_user())
    logger.info("STARTED")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
