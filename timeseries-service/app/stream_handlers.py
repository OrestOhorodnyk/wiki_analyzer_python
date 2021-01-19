import json
import asyncio
import rx

from aiohttp.web import Application
from pymongo.collection import Collection
from pymongo.database import Database
from datetime import datetime
from typing import Dict
from rx.scheduler.eventloop import AsyncIOScheduler
import rx.operators as ops

from .streem import sse_observable


def store_window(item: Dict, db: Database):
    users_collection: Collection = db.get_collection("users")
    recentchanges_collection: Collection = db.get_collection("recentchanges")

    async def save_mongo():
        await users_collection.update_one(
            {"username": item['user']},
            {
                "$setOnInsert": {"username": item['user']},
                "$inc": {"nchanges": item['count']},
            },
            upsert=True,
        )

        if (user := await users_collection.find_one({"username": item['user']})) is not None:
            date = datetime.now().replace(second=0, microsecond=0)

            await recentchanges_collection.find_one_and_update(
                {'d': date, 'u': user['_id']},
                {
                    "$setOnInsert": {"u": user['_id']},
                    '$inc': {'_n': item['count']}
                },
                upsert=True
            )

    asyncio.ensure_future(save_mongo())


class StreamHandler:
    def __init__(self, app: Application):
        self.db: Database = app['mongo']

    async def handle_stream(self):
        try:
            obs = sse_observable('https://stream.wikimedia.org/v2/stream/recentchange')
            scheduler = AsyncIOScheduler(loop=asyncio.get_event_loop())

            obs.pipe(
                ops.map(lambda event: json.loads(event.data)),
                ops.map(lambda x: {'user': x['user']}),
                ops.window(rx.interval(60.)),
                ops.flat_map(lambda wo: wo.pipe(
                    ops.group_by(lambda x: x['user']),
                    ops.flat_map(lambda g: g.pipe(
                        ops.reduce(lambda count, elm: count + 1, 0),
                        ops.map(lambda count: {'user': g.key, 'count': count})
                    )),
                )),
            ).subscribe(lambda data: store_window(data, self.db), scheduler=scheduler)
        except asyncio.CancelledError:
            pass
