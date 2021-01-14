import logging
from typing import Optional

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from websockets.exceptions import ConnectionClosed

from app.stream.recent_changes import get_stream
from app.user_contribytes_service import get_most_active_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/start", status_code=200)
async def get_messages():
    events = get_stream("https://stream.wikimedia.org/v2/stream/recentchange")

    return EventSourceResponse(events)


@router.get("/most_active_user/")
async def most_active_user(year: Optional[int] = None, month: Optional[int] = None, day: Optional[int] = None):
    result = get_most_active_user(year, month, day)
    if result:
        return {
            "User Name": result[0],
            "Activity count": result[1],
            "Activity year": result[2],
            "Activity month": result[3],
            "Activity date": result[4],
        }
    return 'Not found',


@router.websocket_route("/recent_change")
async def recent_change(websocket):
    logger.info("WEBSOKET ACCEPT CONNECTION")
    await websocket.accept()
    msg_txt = await websocket.receive_text()
    logger.info(msg_txt)
    events = get_stream("https://stream.wikimedia.org/v2/stream/recentchange")
    user_set = set()
    async for event in events:
        try:
            msg = 'User: {user} \nEdited article: {title} \n\n'.format(**event)
            await websocket.send_text(msg)
            if len(user_set) < 20:
                user_set.add(event.get('user'))
        except ConnectionClosed:
            logger.info("Connection closed")
            break
    await websocket.close()
    logger.info("WEBSOKET CLOSED")
    logger.info(f"users: {','.join(user_set)}")


@router.websocket_route("/recent_change_by_users")
async def recent_change_by_users(websocket):
    logger.info("WEBSOKET ACCEPT CONNECTION")
    await websocket.accept()
    users = await websocket.receive_text()
    users = users.split(',')
    logger.info(users)
    events = get_stream("https://stream.wikimedia.org/v2/stream/recentchange")
    async for event in events:
        try:
            if event.get('user') in users:
                msg = 'User: {user} \nEdited article: {title} \n\n'.format(**event)
                await websocket.send_text(msg)
        except ConnectionClosed:
            logger.info("Connection closed")
            break
    await websocket.close()
    logger.info("WEBSOKET CLOSED")