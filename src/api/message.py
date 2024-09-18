from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select
import asyncio
import re

from src.models.user import User
from src.models.utils import get_characters_for_story, get_model_configs, get_or_create_uuid

from ..core.config import logger, SENTENCES_PER_SUBTITLE
from ..core.database import get_session
from ..core.websocket import WebsocketManager
from ..models.character import Character
from ..models.story import Story
from ..models.message import Message, MessagePC, MessageNARRATORorSYSTEM
from ..services import audio, imagery, narrator
from ..models.enums import CharacterType, TextModel, AudioModel, ImageModel

router = APIRouter()
socket_manager = WebsocketManager()

@router.websocket('/ws/story/{story_id}')
async def story_websocket(websocket: WebSocket, story_id: int):
    await socket_manager.endpoint(websocket, story_id)

async def generate_audio(text: str, api_key: str, voice_id: str) -> str:
    audio_data = audio.generate(text, api_key=api_key, voice_id=voice_id)
    _, audio_url = audio.store(audio_bytes=audio_data)
    return audio_url

async def handle_narration(narrator_reply: str, soundtrack_path: str, story_id: int, audio_narrator_model: AudioModel, api_key: str, voice_id: str) -> tuple[list[str], list[str]]:
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    # Split the text into sentences
    sentences = sentence_endings.split(narrator_reply)
    # Group sentences into chunks of SENTENCES_PER_SUBTITLE
    narration_chunks = [' '.join(sentences[i:i+SENTENCES_PER_SUBTITLE]) for i in range(0, len(sentences), SENTENCES_PER_SUBTITLE)]

    audio_paths = []
    for narration_chunk in narration_chunks:
        payload = {'message': narration_chunk}
        if audio_narrator_model != AudioModel.none:
            audio_path = await generate_audio(narration_chunk, api_key=api_key, voice_id=voice_id)
            audio_paths.append(audio_path)
            payload['audio_path'] = audio_path
        if soundtrack_path:
            payload['soundtrack_path'] = soundtrack_path
        await socket_manager.broadcast('reply', payload, story_id)
    return narration_chunks, audio_paths

async def handle_image(narrator_reply, story_id, text_model: TextModel, image_model: ImageModel, text_api_key: str, image_api_key: str) -> str | None:
    if image_model != ImageModel.none:
        image_path = await imagery.generate_image(narrator_reply, 'story', text_model=text_model, image_model=image_model, text_api_key=text_api_key, image_api_key=image_api_key)
        await socket_manager.broadcast('reply', {'image_path': image_path}, story_id)
        return image_path
    return None

@router.post('/message', response_model=MessageNARRATORorSYSTEM)
async def generate_message(*, message: MessagePC, session: Session = Depends(get_session)):
    """
    Handle the generation of a message response from the AI narrator.

    Parameters:
    - message: The message sent by the player character.
    - session: The database session dependency.

    Returns:
    - The stored human message instance.
    """
    
    # Broadcast the incoming message to all users
    await socket_manager.broadcast('message', message, message.story_id)
    
    # Get the list of characters in the story
    characters = get_characters_for_story(message.story_id, session)
    
    try:
        # Get the model configurations
        model_configs = get_model_configs(message.story_id, session)
    except HTTPException as e:
        # Log the error and re-raise it
        logger.error(f"Error getting model configs: {e.detail}")
        raise

    # Log model information
    logger.info(f'Text Narrator Model: {model_configs["text"]["model"]}')
    logger.info(f'Audio Narrator Model: {model_configs["audio"]["model"]}')
    logger.info(f'Image Model: {model_configs["image"]["model"]}')

    # Assign model configurations to variables
    text_model = model_configs["text"]["model"]
    text_model_api_key = model_configs["text"]["api_key"]
    audio_model = model_configs["audio"]["model"]
    audio_model_api_key = model_configs["audio"]["api_key"]
    image_model = model_configs["image"]["model"]
    image_model_api_key = model_configs["image"]["api_key"]
    elevenlabs_voice_id = model_configs["audio"]["voice_id"]
    
    # Retrieve the message history for the story
    try:
        messages = session.exec(
            select(Message).where(Message.story_id == message.story_id).order_by(Message.timestamp)
        ).all()
    except Exception as e:
        logger.exception(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while retrieving the message history: {e}')

    runnable = narrator.initialize_or_get_runnable(narrator.prompt, 
                                                   messages, 
                                                   message.story_id, 
                                                   text_model=text_model, 
                                                   api_key=text_model_api_key,
                                                   session=session)    
    
    # if we just ran initialize_runnable, we will most likely have a runnable_uuid
    runnable_uuid = get_or_create_uuid(message.story_id, session)
    character_details = [{"name": character.character_name, "race": character.character_race, "class": character.character_class} for character in characters]
    party_context = ', '.join([f"{detail['name']} (Race: {detail['race']}, Class: {detail['class']})" for detail in character_details])

    
    logger.debug(f'[MESSAGE] {message.message = }')

    character = session.get(Character, message.character_id)
    if character is None:
        raise HTTPException(404, 'Character not found')

    try:
        # Generate the reply first
        narrator_reply, soundtrack_path = narrator.generate_reply(character=character, message=message, runnable=runnable, runnable_uuid=runnable_uuid, party_info=party_context, text_model=text_model)

        # Generate narration and image concurrently and broadcast results as they complete
        narration_task = asyncio.create_task(handle_narration(narrator_reply, soundtrack_path, message.story_id, audio_model, api_key=audio_model_api_key, voice_id=elevenlabs_voice_id))
        image_task = asyncio.create_task(handle_image(narrator_reply, message.story_id, text_model=text_model, image_model=image_model, text_api_key=text_model_api_key, image_api_key=image_model_api_key))

        narration_tuple, image_path = await asyncio.gather(narration_task, image_task)
        subtitles, audio_paths = narration_tuple
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')
    
    human_message = Message(
        story_id=message.story_id,
        character_id=message.character_id,
        character_name=message.character_name,
        character=message.character,
        message=message.message,
        narrator_reply=None,
        audio_path=None,
        image_path=None,
        soundtrack_path=None,
        genai_text_model=text_model,
        genai_audio_model=audio_model,
        genai_image_model=image_model
    )
    session.add(human_message)
    for i in range(len(subtitles)):
        # Create the narrator message entry
        narrator_message = Message(
            story_id=message.story_id,
            character_id=None,  # Assuming narrator doesn't have a character_id
            character_name=CharacterType.narrator,
            character=CharacterType.narrator,
            message=subtitles[i],
            narrator_reply=None,
            audio_path=audio_paths[i] if i < len(audio_paths) else None,
            image_path=image_path,
            soundtrack_path=soundtrack_path,
            genai_text_model=text_model,
            genai_audio_model=audio_model,
            genai_image_model=image_model
        )
        session.add(narrator_message)
        
    session.commit()
    session.refresh(human_message)
    
    return human_message