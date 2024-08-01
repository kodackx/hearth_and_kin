from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select
import asyncio
import re

from ..datamodels.user import User

from ..core.config import logger, SENTENCES_PER_SUBTITLE
from ..core.database import get_session
from ..core.websocket import WebsocketManager
from ..datamodels.character import Character
from ..datamodels.story import Story
from ..datamodels.message import Message, MessagePC, MessageNARRATORorSYSTEM
from ..services import audio, imagery, narrator
from ..core.models import CharacterType, TextModel, AudioModel, ImageModel

router = APIRouter()
socket_manager = WebsocketManager()

@router.websocket('/ws/story/{story_id}')
async def story_websocket(websocket: WebSocket, story_id: int):
    await socket_manager.endpoint(websocket, story_id)

async def generate_audio(model: AudioModel, text: str, api_key: str | dict[str, str]) -> str:
    audio_data = audio.generate(model, text, api_key=api_key)
    _, audio_url = audio.store(audio_bytes=audio_data)
    return audio_url

async def handle_narration(narrator_reply: str, soundtrack_path: str, story_id: int, audio_narrator_model: AudioModel, api_key: str | dict[str, str]) -> tuple[list[str], list[str]]:
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    # Split the text into sentences
    sentences = sentence_endings.split(narrator_reply)
    # Group sentences into chunks of SENTENCES_PER_SUBTITLE
    narration_chunks = [' '.join(sentences[i:i+SENTENCES_PER_SUBTITLE]) for i in range(0, len(sentences), SENTENCES_PER_SUBTITLE)]

    audio_paths = []
    for narration_chunk in narration_chunks:
        payload = {'message': narration_chunk}
        if audio_narrator_model != AudioModel.none:
            audio_path = await generate_audio(audio_narrator_model, narration_chunk, api_key=api_key)
            audio_paths.append(audio_path)
            payload['audio_path'] = audio_path
        if soundtrack_path:
            payload['soundtrack_path'] = soundtrack_path
        await socket_manager.broadcast('reply', payload, story_id)
    return narration_chunks, audio_paths

async def handle_image(narrator_reply, story_id, text_model: TextModel, image_model: ImageModel, api_key: str | dict[str, str]) -> str | None:
    if image_model != ImageModel.none:
        image_path = await imagery.generate_image(narrator_reply, 'story', text_model=text_model, image_model=image_model, api_key=api_key)
        await socket_manager.broadcast('reply', {'image_path': image_path}, story_id)
        return image_path
    return None

@router.post('/message', response_model=MessageNARRATORorSYSTEM)
async def generate_message(*, message: MessagePC, session: Session = Depends(get_session)):
    # Retrieve the story to get model information (that was set in the lobby!)
    story = session.get(Story, message.story_id)
    if not story:
        raise HTTPException(404, 'Story not found')

    text_narrator_model = story.genai_text_model
    audio_narrator_model = story.genai_audio_model
    image_model = story.genai_image_model

    logger.info(f'Text Narrator Model: {text_narrator_model}')
    logger.info(f'Audio Narrator Model: {audio_narrator_model}')
    logger.info(f'Image Model: {image_model}')
    
    
    # Broadcast the incoming message to all users
    await socket_manager.broadcast('message', message, message.story_id)

    # Retrieve the story to get character IDs
    story = session.get(Story, message.story_id)
    if not story:
        raise HTTPException(404, 'Story not found')
    
    character_ids = [story.party_lead, story.party_member_1, story.party_member_2]
    characters = session.exec(
        select(Character).where(Character.character_id.in_(character_ids))
    ).all()

    # Retrieve the user_id from the message
    character = session.exec(
        select(Character).where(Character.character_id == message.character_id)
    ).first()
    if not character:
        raise HTTPException(404, 'Character not found')

    # Retrieve the api keys from the party lead
    party_lead_character = session.get(Character, story.party_lead)
    assert party_lead_character is not None
    party_lead_user = session.get(User, party_lead_character.user_id)
    assert party_lead_user is not None

    party_lead_api_keys = party_lead_user.model_dump()
    # Retrieve the message history for the story
    messages = session.exec(
        select(Message).where(Message.story_id == message.story_id).order_by(Message.timestamp)
    ).all()

    chain = narrator.initialize_chain(narrator.prompt, messages, message.story_id, api_key=party_lead_api_keys, text_model=text_narrator_model)  # type: ignore

    
    character_details = [{"name": character.character_name, "race": character.character_race, "class": character.character_class} for character in characters]
    party_context = ', '.join([f"{detail['name']} (Race: {detail['race']}, Class: {detail['class']})" for detail in character_details])

    
    logger.debug(f'[MESSAGE] {message.message = }')

    character = session.get(Character, message.character_id)
    if character is None:
        raise HTTPException(404, 'Character not found')

    try:
        # Generate the reply first
        narrator_reply, soundtrack_path = narrator.generate_reply(character=character, message=message, chain=chain, party_info=party_context, text_model=text_narrator_model)

        # Generate narration and image concurrently and broadcast results as they complete
        narration_task = asyncio.create_task(handle_narration(narrator_reply, soundtrack_path, message.story_id, audio_narrator_model, api_key=party_lead_api_keys))
        image_task = asyncio.create_task(handle_image(narrator_reply, message.story_id, text_model=text_narrator_model, image_model=image_model, api_key = party_lead_api_keys))

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
        audio_path=None,
        image_path=None,
        soundtrack_path=None
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

            audio_path=audio_paths[i] if i < len(audio_paths) else None,
            image_path=image_path,
            soundtrack_path=soundtrack_path
        )
        session.add(narrator_message)
        
    session.commit()
    session.refresh(human_message)


    return human_message