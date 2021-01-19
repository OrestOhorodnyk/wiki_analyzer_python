from motor.motor_asyncio import AsyncIOMotorClient
from aiohttp.web import Application
from pymongo.database import Database


async def create_mongo(app: Application) -> None:
    settings = app['settings']
    db: Database = AsyncIOMotorClient(settings['mongo_uri'])[settings['db_name']]
    app['mongo'] = db


def setup(app: Application) -> None:
    app.on_startup.append(create_mongo)
