import asyncio
import logging
from datetime import datetime
from typing import Dict

import rx
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


def store_user_contribute_by_title(data: Dict) -> None:
    db = SessionLocal()
    try:
        existing_user_and_title = db.query(
            models.UserContributeByTitle
        ).filter(
            models.UserContributeByTitle.user == data.get('user'),
            models.UserContributeByTitle.title == data.get('title')
        ).first()

        if existing_user_and_title:
            existing_user_and_title.count += data['count']
        else:
            user_contributes = models.UserContributeByTitle(**data)
            db.add(user_contributes)
        db.commit()
    except Exception as err:
        logger.error(f"error {err}")


def store_article_title(data: Dict) -> None:
    db = SessionLocal()
    try:
        existing_user_and_title = db.query(
            models.UserContributeByTitle
        ).filter(
            models.ArticleTitleCount.title == data.get('title'),
        ).first()

        if existing_user_and_title:
            existing_user_and_title.count += data['count']
        else:
            article_title = models.ArticleTitleCount(**data)
            db.add(article_title)
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


def user_contribute_pipeline():
    asyncio.create_task(sse_observable(subject))

    base_transform_pipe = subject.pipe(
        op.map(lambda data: {field: data.get(field) for field in USER_CONTRIBUTES_REQUIRED_FIELDS}),
        op.map(transform_timestamp),
        op.window(rx.interval(30.)),
        op.flat_map(lambda wo: wo.pipe(
            op.group_by(lambda x: (x['user'], x['title'])),
            op.flat_map(lambda g: g.pipe(
                op.reduce(lambda count, elm: count + 1, 0),
                op.map(lambda count: {'user': g.key[0], 'title': g.key[1], 'count': count})
            )),
        ))
    )

    base_transform_pipe.subscribe(
        on_next=store_user_contribute_by_title,
        on_error=lambda e: logger.error("Error Occurred: {0}".format(e))
    )


def title_pipeline():
    asyncio.create_task(sse_observable(subject))

    base_transform_pipe = subject.pipe(
        op.map(lambda data: {field: data.get(field) for field in USER_CONTRIBUTES_REQUIRED_FIELDS}),
        op.filter(lambda c: c['type'] == 'edit' and c['minor']),
        op.window(rx.interval(30.)),
        op.flat_map(lambda wo: wo.pipe(
            op.group_by(lambda x: x['title']),
            op.flat_map(lambda g: g.pipe(
                op.reduce(lambda count, elm: count + 1, 0),
                op.map(lambda count: {'title': g.key, 'count': count})
            )),
        )),
    )

    base_transform_pipe.subscribe(
        on_next=store_article_title,
        on_error=lambda e: logger.error("Error Occurred: {0}".format(e))
    )


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
