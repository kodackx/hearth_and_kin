from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select
import asyncio
import re

from ..core.config import GENERATE_AUDIO, GENERATE_IMAGE, logger, SENTENCES_PER_SUBTITLE, DEFAULT_TEXT_NARRATOR_MODEL, DEFAULT_AUDIO_NARRATOR_MODEL, DEFAULT_IMAGE_MODEL
from ..core.database import get_session
from ..core.websocket import WebsocketManager
from ..models.character import Character
from ..models.story import Story
from ..models.message import Message, MessagePC, MessageNARRATORorSYSTEM
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

async def handle_narration(narrator_reply, soundtrack_path, story_id, audio_narrator_model) -> tuple[list[str], list[str]]:
    print('Will use audio model to generate?')
    print(audio_narrator_model != 'none')

    sentence_endings = re.compile(r'(?<=[.!?]) +')
    # Split the text into sentences
    sentences = sentence_endings.split(narrator_reply)
    # Group sentences into chunks of SENTENCES_PER_SUBTITLE
    narration_chunks = [' '.join(sentences[i:i+SENTENCES_PER_SUBTITLE]) for i in range(0, len(sentences), SENTENCES_PER_SUBTITLE)]

    audio_paths = []
    for narration_chunk in narration_chunks:
        payload = {'message': narration_chunk}
        if (GENERATE_AUDIO and audio_narrator_model != 'none'):
            audio_path = await generate_audio(narration_chunk)
            audio_paths.append(audio_path)
            payload['audio_path'] = audio_path
        if soundtrack_path:
            payload['soundtrack_path'] = soundtrack_path
        await socket_manager.broadcast('reply', payload, story_id)
    return narration_chunks, audio_paths

async def handle_image(narrator_reply, story_id, text_model: str, image_model: str) -> str | None:
    print('Will use image model to generate?')
    print(image_model != 'none')

    if (GENERATE_IMAGE and image_model != 'none'):
        image_path = await imagery.generate_image(narrator_reply, 'story', text_model=text_model, image_model=image_model)
        await socket_manager.broadcast('reply', {'image_path': image_path}, story_id)
        return image_path
    return None

@router.post('/message', response_model=MessageNARRATORorSYSTEM)
async def generate_message(*, message: MessagePC, session: Session = Depends(get_session)):
    # Retrieve the story to get model information (that was set in the lobby!)
    story = session.get(Story, message.story_id)
    if not story:
        raise HTTPException(404, 'Story not found')

    text_narrator_model = story.genai_text_model or DEFAULT_TEXT_NARRATOR_MODEL
    audio_narrator_model = story.genai_audio_model or DEFAULT_AUDIO_NARRATOR_MODEL
    image_model = story.genai_image_model or DEFAULT_IMAGE_MODEL

    print(f'Text Narrator Model: {text_narrator_model}')
    print(f'Audio Narrator Model: {audio_narrator_model}')
    print(f'Image Model: {image_model}')
    
    
    # Broadcast the incoming message to all users
    await socket_manager.broadcast('message', message, message.story_id)

    messages = session.exec(
        select(Message).where(Message.story_id == message.story_id).order_by(Message.timestamp)
    ).all()
    chain = narrator.initialize_chain(narrator.prompt, messages, message.story_id, text_narrator_model)  # type: ignore
    
    # Retrieve the story to get character IDs
    story = session.get(Story, message.story_id)
    if not story:
        raise HTTPException(404, 'Story not found')

    character_ids = [story.party_lead, story.party_member_1, story.party_member_2]
    characters = session.exec(
        select(Character).where(Character.character_id.in_(character_ids))
    ).all()
    
    character_details = [{"name": character.character_name, "race": character.character_race, "class": character.character_class} for character in characters]
    party_context = ', '.join([f"{detail['name']} (Race: {detail['race']}, Class: {detail['class']})" for detail in character_details])

    
    logger.debug(f'[MESSAGE] {message.message = }')
    # Not sure if we want to get this from the endpoint or just query the db here
    character = session.get(Character, message.character_id)
    if character is None:
        raise HTTPException(404, 'Character not found')

    try:
        # Generate the reply first
        narrator_reply, soundtrack_path = narrator.generate_reply(character=character, message=message, chain=chain, party_info=party_context, model=text_narrator_model)

        # Generate narration and image concurrently and broadcast results as they complete
        narration_task = asyncio.create_task(handle_narration(narrator_reply, soundtrack_path, message.story_id, audio_narrator_model))
        image_task = asyncio.create_task(handle_image(narrator_reply, message.story_id, text_model=text_narrator_model, image_model=image_model))

        narration_tuple, image_path = await asyncio.gather(narration_task, image_task)
        subtitles, audio_paths = narration_tuple
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')
    
    human_message = Message(
        story_id=message.story_id,
        character_id=message.character_id,
        character_name=message.character_name,
        character=message.character, #could be NARRATOR, PC or SYSTEM
        message=message.message,
        narrator_reply=None,
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
            character_name="NARRATOR",
            character="NARRATOR", #could be NARRATOR, PC or SYSTEM
            message=subtitles[i],
            narrator_reply=None,
            audio_path=audio_paths[i] if i < len(audio_paths) else None,
            image_path=image_path,
            soundtrack_path=soundtrack_path
        )
        session.add(narrator_message)
        
    session.commit()
    session.refresh(human_message)


    return human_message
