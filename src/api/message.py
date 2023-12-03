from fastapi import APIRouter, Response, status
from ..models.message import MessageRead, Message, MessageBase
from ..core.config import logger
from ..services import audio, imagery
from ..core.database import Session, engine
import requests

router = APIRouter()


@router.post('/message', response_model=MessageRead)
def generate_message(message: MessageBase, response: Response):
    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    logger.debug(f'[MESSAGE] {message.message = }')
    # Will send to openai and obtain reply
    narrator_reply = requests.post('http://openai-api-url', json={'input': message.message}).json()
    # Will send to narrator and obtain audio
    audio_path = audio.obtain_audio(narrator_reply)
    narrator_audio = audio.send_audio(audio_path)
    # Will send to dalle3 and obtain image
    background_path = imagery.generate_image(narrator_reply)
    logger.debug(f'[MESSAGE] {background_path = }')
    background_image = imagery.obtain_image_from_url(background_path)
    logger.debug(f'[MESSAGE] {background_image = }')
    # Will send to user
    # TODO: Replace socketio.emit with the appropriate method to send data to the client
    # socketio.emit('new_message', {'message': 'Openai reply: '})
    with Session(engine) as session:
        new_message = Message(
            message=message.message, narrator_reply=narrator_reply, audio=narrator_audio, image=background_path
        )
        session.add(new_message)
        session.commit()
        session.refresh(new_message)
        response.status_code = status.HTTP_201_CREATED
        return new_message
