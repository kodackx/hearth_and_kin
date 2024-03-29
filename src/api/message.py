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
    audio_id = audio_path = image_url = image_path = soundtrack_path = narrator_reply = None
    try:
        logger.debug(f'[MESSAGE] {message.message = }')
        # Not sure if we want to get this from the endpoint or just query the db here
        character = session.get(Character, message.character_id)
        if character is None:
            raise HTTPException(404, 'Character not found')
        # Will send to openai and obtain reply
        if GENERATE_REPLY:
            narrator_reply = narrator.gpt_narrator(character=character, message=message, chain=chain)
        soundtrack_directives = ['[SOUNDTRACK: ambiance.m4a]', '[SOUNDTRACK: cozy_tavern.m4a]', '[SOUNDTRACK: wilderness.m4a]']
        for directive in soundtrack_directives:
            if directive in narrator_reply:
                # Handle the soundtrack directive here
                # For example, log it or set a path to the soundtrack file
                logger.debug(f'[MESSAGE] Soundtrack directive found: {directive}')
                # Extract the soundtrack name from the directive
                soundtrack_name = directive.strip('[]').split(': ')[1]
                # Assuming you have a method to get the path of the soundtrack
                soundtrack_path = f'/azure/public/soundtracks/{soundtrack_name}'
                logger.debug(f'[MESSAGE] Soundtrack path: {soundtrack_path}')
                # Remove the directive from the narrator_reply to clean up the final message
                narrator_reply = narrator_reply.replace(directive, '').strip()
                break  # Assuming only one soundtrack directive per reply, break after handling the first one found

            if GENERATE_AUDIO:  # Will send to narrator and obtain audio
                audio_id, audio_url = audio.generate(narrator_reply)
            if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
                image_url = imagery.generate(narrator_reply)
                logger.debug(f'[MESSAGE] {image_url = }')
                image_id, image_url = await imagery.store(image_url, 'story')
                logger.debug(f'[MESSAGE] {image_path = }')
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
