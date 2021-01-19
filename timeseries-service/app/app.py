import os
import asyncio
from pathlib import Path
from aiohttp import web
from aiohttp.web_app import Application

from .mongo import setup as mongo_setup
import logging

from .utils import load_config
from .stream_handlers import StreamHandler

PROJ_ROOT = Path(__file__).parent.parent
logger = logging.getLogger(__name__)
ENV = os.getenv('ENV', 'debug').lower()


async def start_background_tasks(app):
    handler = StreamHandler(app)
    app['sse_listener'] = asyncio.create_task(handler.handle_stream())


async def cleanup_background_tasks(app):
    app['sse_listener'].cancel()
    await app['sse_listener']


def create_app() -> web.Application:
    logging.basicConfig(level=logging.INFO, datefmt='[%H:%M:%S]')

    config_filename = 'config.yml' if ENV == 'debug' else f"config.yml.{ENV}"

    logger.info(f"Running on {ENV} environment")

    app: Application = web.Application(logger=logger)
    settings = load_config(os.path.join(PROJ_ROOT, config_filename))
    app['settings'] = settings
    mongo_setup(app)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    return app
