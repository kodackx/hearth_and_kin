from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session, select
import asyncio
import re

from ..core.config import GENERATE_AUDIO, GENERATE_IMAGE, logger, SENTENCES_PER_SUBTITLE, DEFAULT_TEXT_NARRATOR_MODEL, DEFAULT_TEXT_IMAGE_MODEL, DEFAULT_IMAGE_MODEL
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

async def handle_narration(narrator_reply, soundtrack_path, story_id) -> tuple[list[str], list[str]]:
    sentence_endings = re.compile(r'(?<=[.!?]) +')
    # Split the text into sentences
    sentences = sentence_endings.split(narrator_reply)
    # Group sentences into chunks of SENTENCES_PER_SUBTITLE
    narration_chunks = [' '.join(sentences[i:i+SENTENCES_PER_SUBTITLE]) for i in range(0, len(sentences), SENTENCES_PER_SUBTITLE)]

    audio_paths = []
    for narration_chunk in narration_chunks:
        payload = {'message': narration_chunk}
        if GENERATE_AUDIO:
            audio_path = await generate_audio(narration_chunk)
            audio_paths.append(audio_path)
            payload['audio_path'] = audio_path
        if soundtrack_path:
            payload['soundtrack_path'] = soundtrack_path
        await socket_manager.broadcast('reply', payload, story_id)
    return narration_chunks, audio_paths

async def handle_image(narrator_reply, story_id, text_model: str, image_model: str) -> str | None:
    if GENERATE_IMAGE:
        image_path = await imagery.generate_image(narrator_reply, 'story', text_model=text_model, image_model=image_model)
        await socket_manager.broadcast('reply', {'image_path': image_path}, story_id)
        return image_path
    return None

@router.post('/message', response_model=MessageNARRATORorSYSTEM)
async def generate_message(*, message: MessagePC, session: Session = Depends(get_session)):
    text_image_model = message.text_image_model or DEFAULT_TEXT_IMAGE_MODEL
    image_model = message.image_model or DEFAULT_IMAGE_MODEL
    text_narrator_model = message.text_narrator_model or DEFAULT_TEXT_NARRATOR_MODEL
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

    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    audio_url = image_url = soundtrack_path = narrator_reply = None
    try:
        # Generate the reply first
        narrator_reply, soundtrack_path = narrator.generate_reply(character=character, message=message, chain=chain, party_info=party_context, model=text_narrator_model)

            narrator_reply = narrator.gpt_narrator(character=character, message=message, chain=chain, party_info=party_context)
            soundtrack_directives = ['[SOUNDTRACK: ambiance.m4a]', '[SOUNDTRACK: cozy_tavern.m4a]', '[SOUNDTRACK: wilderness.m4a]']
            for directive in soundtrack_directives:
                if directive in narrator_reply:
                    # Handle the soundtrack directive here
                    # For example, log it or set a path to the soundtrack file
                    logger.debug(f'[MESSAGE] Soundtrack directive found: {directive}')
                    # Extract the soundtrack name from the directive
                    soundtrack_name = directive.strip('[]').split(': ')[1]
                    # Assuming you have a method to get the path of the soundtrack
                    soundtrack_path = f'/static/soundtrack/{soundtrack_name}'
                    logger.debug(f'[MESSAGE] Soundtrack path: {soundtrack_path}')
                    # Remove the directive from the narrator_reply to clean up the final message
                    narrator_reply = narrator_reply.replace(directive, '').strip()
                    break  # Assuming only one soundtrack directive per reply, break after handling the first one found

        # Generate narration and image concurrently and broadcast results as they complete
        narration_task = asyncio.create_task(handle_narration(narrator_reply, soundtrack_path, message.story_id))
        image_task = asyncio.create_task(handle_image(narrator_reply, message.story_id, text_model=text_image_model, image_model=image_model))

        narration_tuple, image_path = await asyncio.gather(narration_task, image_task)
        subtitles, audio_paths = narration_tuple
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        raise HTTPException(500, f'An error occurred while generating the response: {e}')
    
    # Create the human message entry
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
    session.commit()
    session.refresh(human_message)

    # Create the narrator message entry
    narrator_message = Message(
        story_id=message.story_id,
        character_id=None,  # Assuming narrator doesn't have a character_id
        character_name="NARRATOR",
        character="NARRATOR", #could be NARRATOR, PC or SYSTEM
        message=narrator_reply or 'Narrator says hi',
        narrator_reply=None,
        audio_path=audio_url,
        image_path=image_url,
        soundtrack_path=soundtrack_path
    )
    session.add(narrator_message)
    session.commit()
    session.refresh(narrator_message)

    # Broadcast the narrator's reply
    websocket_message = MessageNARRATORorSYSTEM.model_validate(narrator_message).model_dump(exclude='timestamp')
    await socket_manager.broadcast('reply', websocket_message, message.story_id)

    return human_message
