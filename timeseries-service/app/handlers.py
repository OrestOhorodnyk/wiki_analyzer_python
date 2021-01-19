import asyncio
from aiohttp import web
from aiohttp.web import Application
from pymongo.collection import Collection
from .streem import get_stream
from datetime import datetime
import pymongo


class APIHandler:
    async def health(self, request):
        return web.json_response({"status": "healthy"})

    async def get_top_contributors(self, request):
        db = request.app['mongo']
        limit = int(request.query.get('limit', 100))

        user_collection: Collection = db.get_collection('users')
        data = user_collection.find({}, sort=[('nchanges', pymongo.DESCENDING)], projection={'_id': 0})

        return web.json_response(await data.to_list(length=limit))

    async def chart_user_contribution(self, request):
        db = request.app['mongo']
        users_collection: Collection = db.get_collection("users")

        username = request.match_info['username']
        limit = int(request.query.get('limit', 100))

        if (user := await users_collection.find_one({'username': username})) is None:
            return web.json_response(data={"message": f"Not found: {username}"}, status=404)

        # available_date_granularity = [
        #     'month','week','day','hour','minute'
        # ]

        pipeline = [
            {
                "$match": {"u": user['_id']}
            },
            {
                "$group": {
                    "_id": {
                        "$add": [
                            {"$dayOfYear": "$d"},
                            {"$hour": "$d"},
                            # {"$minute": "$d"},
                        ]
                    },
                    "count": {"$sum": "$_n"},
                    "first": {"$min": "$d"},
                },
            },
            {
                "$limit": limit
            },
            {
                "$sort": {
                    "first.year": 1,
                    "first.dayOfYear": 1,
                    "first.hour": 1,
                    "first.minute": 1,
                    "first.second": 1,
                }
            },
            {
                "$project": {"date": "$first", "count": 1, "_id": 0}
            }
        ]

        cursor = db.get_collection('recentchanges').aggregate(pipeline)
        data = []
        async for item in cursor:
            data.append({
                'x': item['date'].isoformat(),
                'y': item['count']
            })

        return web.json_response({'data': data})


async def handle_stream(app: Application):
    try:
        recentchanges_collection: Collection = app['mongo'].get_collection("recentchanges")
        users_collection: Collection = app['mongo'].get_collection("users")

        events = get_stream("https://stream.wikimedia.org/v2/stream/recentchange")

        async for event in events:
            await users_collection.update_one(
                {"username": event['user']},
                {
                    "$setOnInsert": {"username": event['user']},
                    "$inc": {"nchanges": 1},
                },
                upsert=True,
            )
            user_id = await users_collection.find_one({"username": event['user']})

            date = datetime.fromisoformat(event['meta']['dt'].replace('Z', '+00:00')).replace(second=0, microsecond=0)

            await recentchanges_collection.find_one_and_update(
                {'d': date, 'u': user_id['_id']},
                {
                    "$setOnInsert": {"u": user_id['_id']},
                    '$inc': {'_n': 1}
                },
                upsert=True
            )
    except asyncio.CancelledError:
        pass
