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

        available_date_granularity = ['year', 'month', 'day', 'hour']

        date_granularity = request.query.get('granularity', 'year')

        if date_granularity not in available_date_granularity:
            return web.json_response(data={"message": f"Not available date granularity: {date_granularity}"},
                                     status=401)

        granularity_params = {
            'year': {'g': {"year": {"$year": "$d"}}, 's': {"_id.year": 1}},
            'month': {'g': {"month": {"$month": "$d"}}, 's': {"_id.month": 1}},
            'day': {'g': {"day": {"$dayOfMonth": "$d"}}, 's': {"_id.day": 1}},
            'hour': {'g': {"hour": {"$hour": "$d"}}, 's': {"_id.hour": 1}},
        }

        pipeline = [
            {
                "$match": {"u": user['_id']}
            },
            {
                "$group": {
                    "_id": granularity_params[date_granularity]['g'],
                    "count": {"$sum": "$_n"},
                    "date": {"$min": "$d"},
                },
            },
            {
                "$limit": limit
            },
            {
                "$sort": granularity_params[date_granularity]['s']
            }
        ]

        cursor = db.get_collection('recentchanges').aggregate(pipeline)
        data = []
        async for item in cursor:
            year = item['_id'].get('year', item['date'].year)
            month = item['_id'].get('month', item['date'].month)
            day = item['_id'].get('day', item['date'].day)
            hour = item['_id'].get('hour', item['date'].hour)

            data.append({
                'x': datetime(year, month, day, hour).isoformat(),
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
