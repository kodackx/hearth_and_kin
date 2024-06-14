from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select
import asyncio

from ..core.config import GENERATE_AUDIO, GENERATE_IMAGE, logger
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

async def generate_audio(text: str) -> str:
    audio_data = audio.generate(text)
    _, audio_url = audio.store(audio_bytes=audio_data)
    return audio_url

async def handle_narration(narrator_reply, soundtrack_path, story_id) -> tuple[list[str], list[str]]:
    narration_chunks = narrator_reply.split("\n\n")
    audio_paths = []
    for narration_chunk in narration_chunks:
        payload = {'narrator_reply': narration_chunk}
        if GENERATE_AUDIO:
            audio_path = await generate_audio(narration_chunk)
            audio_paths.append(audio_path)
            payload['audio_path'] = audio_path
        if soundtrack_path:
            payload['soundtrack_path'] = soundtrack_path
        await socket_manager.broadcast('reply', payload, story_id)
    return narration_chunks, audio_paths

async def handle_image(narrator_reply, story_id) -> str | None:
    if GENERATE_IMAGE:
        image_path = await imagery.generate_image(narrator_reply)
        await socket_manager.broadcast('reply', {'image_path': image_path}, story_id)
        return image_path
    return None

@router.post('/message')
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

        # Generate narration and image concurrently and broadcast results as they complete
        narration_task = asyncio.create_task(handle_narration(narrator_reply, soundtrack_path, message.story_id))
        image_task = asyncio.create_task(handle_image(narrator_reply, message.story_id))

        narration_tuple, image_path = await asyncio.gather(narration_task, image_task)
        subtitles, audio_paths = narration_tuple
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')
    
    for i in range(len(subtitles)):
        new_message = Message(
            story_id=message.story_id,
            character_id=message.character_id,
            character_name=message.character_name,
            message=message.message,
            narrator_reply=subtitles[i],
            audio_path=audio_paths[i],
            image_path=image_path,
            soundtrack_path=soundtrack_path
        )
        session.add(new_message)
        session.commit()
        session.refresh(new_message)
