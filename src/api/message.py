from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select

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

@router.post('/message', response_model=MessageRead)
async def generate_message(*, message: MessageBase, session: Session = Depends(get_session)):
    # Broadcast the incoming message to all users
    await socket_manager.broadcast('message', message, message.story_id)

    messages = session.exec(select(Message).where(Message.story_id == message.story_id)).all()
    chain = narrator.initialize_chain(narrator.prompt, messages)  # type: ignore
    
    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    audio_url = image_url = soundtrack_path = narrator_reply = None
    try:
        logger.debug(f'[MESSAGE] {message.message = }')
        # Not sure if we want to get this from the endpoint or just query the db here
        character = session.get(Character, message.character_id)
        if character is None:
            raise HTTPException(404, 'Character not found')
        # Will send to openai and obtain reply
        if GENERATE_REPLY:
            logger.debug('[MESSAGE] generating reply')
            narrator_reply, soundtrack_path = narrator.generate_reply(character, message, chain)
            logger.debug(f'[MESSAGE] {narrator_reply = }')
            if GENERATE_AUDIO:  # Will send to narrator and obtain audio
                audio_url = await audio.generate_audio(narrator_reply)
            if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
                logger.debug('[MESSAGE] generating image')
                image_url = await imagery.generate_image(narrator_reply)
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
        soundtrack_path=soundtrack_path
    )
    session.add(new_message)
    session.commit()
    session.refresh(new_message)

    # Timestamp field is not json serializable by websocket, exclude it here before passing to websocket
    websocket_message = MessageRead.model_validate(new_message).model_dump(exclude='timestamp')
    await socket_manager.broadcast('reply', websocket_message, message.story_id)

    return new_message
