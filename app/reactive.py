import asyncio
import logging

from rx.subject import Subject
from rx import operators as op
from app.stream.recent_changes import get_stream
from datetime import datetime
from typing import Dict
from app.db.database import SessionLocal, engine
from app.db import models
from app.constants import USER_CONTRIBUTES_REQUIRED_FIELDS

logger = logging.getLogger(__name__)


def store_user_contributes(data: Dict) -> None:
    db = SessionLocal()

    try:
        user_contributes = models.UserContributes(**data)
        db.add(user_contributes)
        db.commit()
    except Exception as err:
        logger.error(f"error {err}")


async def sse_observable(observable):
    events = get_stream("https://stream.wikimedia.org/v2/stream/recentchange")

    async for event in events:
        observable.on_next(event)


def transform_timestamp(data):
    data["timestamp"] = datetime.fromtimestamp(data["timestamp"])

    return data


def handle_source():
    subject = Subject()
    asyncio.create_task(sse_observable(subject))

    base_transform_pipe = subject.pipe(
        op.map(lambda data: {field: data.get(field) for field in USER_CONTRIBUTES_REQUIRED_FIELDS}),
        op.map(transform_timestamp)
    )
    base_transform_pipe.subscribe(store_user_contributes)
    base_transform_pipe.subscribe(lambda data: logger.info(f"User: {data['user']} \nEdited article: {data['title']}"))
