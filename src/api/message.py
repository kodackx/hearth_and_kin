from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from ..models.character import CharacterRead

from ..core.config import logger, GENERATE_IMAGE, GENERATE_AUDIO
from ..core.database import get_session
from ..core.mongodb import setup_mongodb
from ..models.message import Message, MessageBase
from ..services import audio, imagery, narrator

router = APIRouter()
mongodb = setup_mongodb()


@router.post('/message')
async def generate_message(*, character: CharacterRead, message: MessageBase, session: Session = Depends(get_session)):
    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    audio_id = audio_path = background_path = background_image = None
    try:
        logger.debug(f'[MESSAGE] {message.message = }')

        # Will send to openai and obtain reply
        narrator_reply = narrator.gpt_narrator(character=character, message=message, chain=narrator.chat_llm_chain)

        if GENERATE_AUDIO:  # Will send to narrator and obtain audio
            audio_id, audio_path = audio.obtain_audio(narrator_reply)
            _ = await audio.store_audio(audio_id, audio_path)
            if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
                background_path = imagery.generate_image(narrator_reply)
                logger.debug(f'[MESSAGE] {background_path = }')
                background_image = imagery.obtain_image_from_url(background_path)
                logger.debug(f'[MESSAGE] {background_image = }')
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')
    # Will send to user
    # TODO: Replace socketio.emit with the appropriate method to send data to the client
    # socketio.emit('new_message', {'message': 'Openai reply: '})
    new_message = Message(
        story_id=message.story_id,
        character_id=character.character_id,
        username=message.username,
        message=message.message,
        narrator_reply=narrator_reply,
        audio_path=audio_path,
        image_path=background_path,
    )
    logger.debug(f'{new_message = }')
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    return new_message
