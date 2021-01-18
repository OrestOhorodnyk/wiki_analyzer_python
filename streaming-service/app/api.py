import logging

from fastapi import APIRouter
from websockets.exceptions import ConnectionClosed

from app.reactive import subject, to_agen
from app.stream.recent_changes import get_stream

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def status():
    return {"status": "ok"}


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


@router.websocket_route("/recent_typos")
async def recent_typos(websocket):
    logger.info("WEBSOKET ACCEPT CONNECTION")
    await websocket.accept()
    async for event in to_agen(subject):
        msg = 'Is minor: {minor} \n\n'.format(
            minor=False if 'minor' not in event else event['minor']
        )
        await websocket.send_text(msg)
    await websocket.close()
    logger.info("WEBSOKET CLOSED")


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
