import logging
import asyncio
import functools

import aiohttp
import rx
from aiohttp_sse_client import client as sse_client
from rx.disposable import Disposable
from rx import Observable

logger = logging.getLogger(__name__)


def sse_observable(url: str) -> Observable:
    def on_subscribe(observer, scheduler):
        loop = asyncio.get_event_loop()

        timeout = aiohttp.ClientTimeout(total=-1)
        session = aiohttp.ClientSession(timeout=timeout)

        async def _aio_sub():
            async with sse_client.EventSource(url, session=session) as event_source:
                try:
                    async for event in event_source:
                        observer.on_next(event)
                        # loop.call_soon(observer.on_completed)
                except Exception as e:
                    loop.call_soon(functools.partial(observer.on_error, e))

        task = asyncio.ensure_future(_aio_sub(), loop=loop)
        return Disposable(lambda: task.cancel())

    return rx.create(on_subscribe)
