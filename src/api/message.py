from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from ..models.character import Character

from ..core.config import logger, GENERATE_IMAGE, GENERATE_AUDIO
from ..core.database import get_session
from ..models.message import Message, MessageBase, MessageRead
from ..services import audio, imagery, narrator

router = APIRouter()

@router.post('/message', response_model=MessageRead)
async def generate_message(*, message: MessageBase, session: Session = Depends(get_session)):
    # TODO: do we have to recreate the chain at every call? Possible to cache this?
    messages = session.exec(select(Message).where(Message.story_id == message.story_id)).all()
    chain_openai = narrator.initialize_chain(narrator.prompt, messages) 
    chain_groq = narrator.initialize_chain_groq(narrator.prompt, messages)

    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    audio_id = audio_path = image_url = image_path = soundtrack_path = None
    try:
        logger.debug(f'[MESSAGE] {message.message = }')
        # Not sure if we want to get this from the endpoint or just query the db here
        character = session.get(Character, message.character_id)
        if character is None:
            raise HTTPException(404, 'Character not found')
        # Choose chain
        chain = chain_groq
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
                soundtrack_path = f'/static/soundtrack/{soundtrack_name}'
                logger.debug(f'[MESSAGE] Soundtrack path: {soundtrack_path}')
                # Remove the directive from the narrator_reply to clean up the final message
                narrator_reply = narrator_reply.replace(directive, '').strip()
                break  # Assuming only one soundtrack directive per reply, break after handling the first one found

        if GENERATE_AUDIO:  # Will send to narrator and obtain audio
            audio_id, audio_path = await audio.obtain_audio(narrator_reply)
        if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
            # choose model between dalle3 and stability
            model = 'stability'
            image_url = await imagery.generate_image(narrator_reply, model)
            logger.debug(f'[MESSAGE] {image_url = }')
            image_path = await imagery.store_image(image_url, 'story', model)
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
        soundtrack_path=soundtrack_path
    )
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    return new_message
