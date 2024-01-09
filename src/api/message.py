from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketException
from sqlmodel import Session, select

from ..core.config import GENERATE_AUDIO, GENERATE_IMAGE, logger
from ..core.database import get_session
from ..models.character import Character
from ..models.message import Message, MessageBase, MessageRead
from ..services import audio, imagery, narrator

router = APIRouter()

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket('/ws/prompt')
async def generate_reply(websocket: WebSocket, session: Session = Depends(get_session)):
    await manager.connect(websocket)
    
    while True:
        message = await websocket.receive_json()
        logger.debug(f'[MESSAGE] {message = }')
        message: MessageBase = MessageBase.model_validate(message)
        # TODO: do we have to recreate the chain at every call? Possible to cache this?
        messages = session.exec(select(Message).where(Message.story_id == message.story_id)).all()
        chain = narrator.initialize_chain(narrator.prompt, messages)  # type: ignore

        # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
        audio_id = audio_path = image_url = image_path = None
        try:
            logger.debug(f'[MESSAGE] {message.message = }')
            # Not sure if we want to get this from the endpoint or just query the db here
            character = session.get(Character, message.character_id)
            if character is None:
                raise WebSocketException(404, 'Character not found')
            # Will send to openai and obtain reply
            narrator_reply = narrator.gpt_narrator(character=character, message=message, chain=chain)

            if GENERATE_AUDIO:  # Will send to narrator and obtain audio
                audio_id, audio_path = audio.obtain_audio(narrator_reply)
                _ = await audio.store_audio(audio_id, audio_path)
            if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
                image_url = imagery.generate_image(narrator_reply)
                logger.debug(f'[MESSAGE] {image_url = }')
                image_path = await imagery.store_image(image_url)
                logger.debug(f'[MESSAGE] {image_path = }')
        except Exception as e:
            logger.error(f'[MESSAGE] {e}')
            raise WebSocketException(500, f'An error occurred while generating the response: {e}')
            #raise HTTPException(500, f'An error occurred while generating the response: {e}')

        new_message = Message(
            story_id=message.story_id,
            character_id=message.character_id,
            username=message.username,
            message=message.message,
            narrator_reply=narrator_reply,
            audio_path=audio_path,
            image_path=image_path,
        )
        session.add(new_message)
        session.commit()
        session.refresh(new_message)

        await manager.broadcast(new_message.model_dump_json())


@router.post('/message', response_model=MessageRead)
async def generate_message(*, message: MessageBase, session: Session = Depends(get_session)):
    # TODO: do we have to recreate the chain at every call? Possible to cache this?
    messages = session.exec(select(Message).where(Message.story_id == message.story_id)).all()
    chain = narrator.initialize_chain(narrator.prompt, messages)  # type: ignore

    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    audio_id = audio_path = image_url = image_path = None
    try:
        logger.debug(f'[MESSAGE] {message.message = }')
        # Not sure if we want to get this from the endpoint or just query the db here
        character = session.get(Character, message.character_id)
        if character is None:
            raise HTTPException(404, 'Character not found')
        # Will send to openai and obtain reply
        narrator_reply = narrator.gpt_narrator(character=character, message=message, chain=chain)

        if GENERATE_AUDIO:  # Will send to narrator and obtain audio
            audio_id, audio_path = audio.obtain_audio(narrator_reply)
            _ = await audio.store_audio(audio_id, audio_path)
        if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
            image_url = imagery.generate_image(narrator_reply)
            logger.debug(f'[MESSAGE] {image_url = }')
            image_path = await imagery.store_image(image_url)
            logger.debug(f'[MESSAGE] {image_path = }')
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')

    new_message = Message(
        story_id=message.story_id,
        character_id=message.character_id,
        username=message.username,
        message=message.message,
        narrator_reply=narrator_reply,
        audio_path=audio_path,
        image_path=image_path,
    )
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    
    return new_message
