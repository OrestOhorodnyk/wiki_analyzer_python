import json
import logging

from aiohttp_sse_client import client as sse_client

logger = logging.getLogger(__name__)


async def get_stream(url_from: str):
    async with sse_client.EventSource(
            url_from
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
            print(error)
            logger.error(f"Error occurred: {error}")
            raise
