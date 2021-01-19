import json
import logging

import aiohttp
from aiohttp_sse_client import client as sse_client

logger = logging.getLogger(__name__)


async def get_stream(url_from: str):
    timeout = aiohttp.ClientTimeout(total=-1)
    session = aiohttp.ClientSession(timeout=timeout)

    async with sse_client.EventSource(
            url_from,
            session=session
    ) as event_source:
        try:
            async for event in event_source:
                try:
                    change = json.loads(event.data)
                except ValueError:
                    pass
                else:
                    yield change
        except Exception as error:
            logger.error(f"Error occurred: {error}")
