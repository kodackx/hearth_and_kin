from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select
import asyncio

from ..core.config import GENERATE_AUDIO, GENERATE_IMAGE, GENERATE_REPLY, logger
from ..core.database import get_session
from ..core.websocket import WebsocketManager
from ..models.character import Character
from ..models.message import Message, MessageBase, MessageRead
from ..services import audio, imagery, narrator

router = APIRouter()
socket_manager = WebsocketManager()

@router.websocket('/ws/story/{story_id}')
async def story_websocket(websocket: WebSocket, story_id: int):
    await socket_manager.endpoint(websocket, story_id)

async def handle_audio(narrator_reply, story_id):
    if GENERATE_AUDIO:
        audio_url = await audio.generate_audio(narrator_reply)
        await socket_manager.broadcast('reply', {'audio_url': audio_url}, story_id)
        return audio_url
    return None

async def handle_image(narrator_reply, story_id):
    if GENERATE_IMAGE:
        image_url = await imagery.generate_image(narrator_reply)
        await socket_manager.broadcast('reply', {'image_url': image_url}, story_id)
        return image_url
    return None

@router.post('/message', response_model=MessageRead)
async def generate_message(*, message: MessageBase, session: Session = Depends(get_session)):
    # Broadcast the incoming message to all users
    await socket_manager.broadcast('message', message, message.story_id)

    messages = session.exec(select(Message).where(Message.story_id == message.story_id)).all()
    chain = narrator.initialize_chain(narrator.prompt, messages)  # type: ignore
    
    logger.debug(f'[MESSAGE] {message.message = }')
    # Not sure if we want to get this from the endpoint or just query the db here
    character = session.get(Character, message.character_id)
    if character is None:
        raise HTTPException(404, 'Character not found')
        
    try:
        # Generate the reply first
        narrator_reply, soundtrack_path = narrator.generate_reply(character, message, chain)
        logger.debug(f'[MESSAGE] {soundtrack_path = }')
        await socket_manager.broadcast('reply', {'narrator_reply': narrator_reply}, message.story_id)
        if soundtrack_path:
            await socket_manager.broadcast('reply', {'soundtrack_path': soundtrack_path}, message.story_id)

        # Generate audio and image concurrently and broadcast results as they complete
        audio_task = asyncio.create_task(handle_audio(narrator_reply, message.story_id))
        image_task = asyncio.create_task(handle_image(narrator_reply, message.story_id))

        audio_url, image_url = await asyncio.gather(audio_task, image_task)
        
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')
    
    new_message = Message(
        story_id=message.story_id,
        character_id=message.character_id,
        character_name=message.character_name,
        message=message.message,
        narrator_reply=narrator_reply or 'Narrator says hi',
        audio_path=audio_url,
        image_path=image_url,
        soundtrack_path=soundtrack_path or None
    )
    session.add(new_message)
    session.commit()
    session.refresh(new_message)

    # Timestamp field is not json serializable by websocket, exclude it here before passing to websocket
    websocket_message = MessageRead.model_validate(new_message).model_dump(exclude='timestamp')
    await socket_manager.broadcast('reply', websocket_message, message.story_id)

    return new_message
