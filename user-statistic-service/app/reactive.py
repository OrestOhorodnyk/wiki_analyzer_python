import asyncio
import logging
from datetime import datetime
from typing import Dict

from rx import operators as op
from rx.core.notification import OnNext, OnError
from rx.scheduler.eventloop import AsyncIOScheduler
from rx.subject import Subject

from app.constants import USER_CONTRIBUTES_REQUIRED_FIELDS
from app.db import models
from app.db.database import SessionLocal
from app.stream.recent_changes import get_stream

logger = logging.getLogger(__name__)

subject = Subject()


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
    asyncio.create_task(sse_observable(subject))

    base_transform_pipe = subject.pipe(
        op.map(lambda data: {field: data.get(field) for field in USER_CONTRIBUTES_REQUIRED_FIELDS}),
        op.map(transform_timestamp)
    )
    base_transform_pipe.subscribe(store_user_contributes)
    # base_transform_pipe.subscribe(lambda data: logger.info(f"User: {data['user']} \nEdited article: {data['title']}"))


async def to_agen(obs):
    queue = asyncio.Queue()

    def on_next(i):
        queue.put_nowait(i)

    disposable = obs.pipe(op.materialize()).subscribe(
        on_next=on_next,
        scheduler=AsyncIOScheduler(loop=asyncio.get_event_loop())
    )

    while True:
        i = await queue.get()
        if isinstance(i, OnNext):
            yield i.value
            queue.task_done()
        elif isinstance(i, OnError):
            disposable.dispose()
            raise (Exception(i.value))
        else:
            disposable.dispose()
            break
