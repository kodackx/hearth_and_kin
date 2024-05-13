from fastapi import APIRouter, Response, status, Depends, HTTPException
from ..core.database import get_session
from sqlmodel import Session
from ..models.message import Message, MessageBase
from ..models.character import CharacterBase, Character, CharacterCreate, CharacterRead, CharacterUpdate, CharacterCreateMessage
from ..core.config import logger
from ..services import audio, imagery
from ..core.database import engine
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from sqlmodel import Session
import random
from pydantic import ValidationError
import re

router = APIRouter()

prompt_narrator = """
The player is starting a new journey in Hearth and Kin, a game inspired from Dungeons and Dragons.
You must act like a primordial being that exists in the mists of an ancient forest, and whispers to the player to guide them in creating a new character for a story.

Take them step by step and guide them as noted below:
-
From the mists of primordial space, where the planets dance in a celestial waltz, your character emerges. Begin to weave the tapestry of their existence.
Envision them in the vastness of this universe. Who are they? What race do they belong to – are they a stoic Dwarf, a mystical Elf, a resourceful Human, or perhaps something more arcane? Let the stars whisper their race to your mind.
Now, think of their class. Are they a brave Warrior, a cunning Rogue, or a wise Wizard? Each class carries its own destiny. What path does your character tread upon?
Delve deeper into their essence. What is their name – a name that echoes in the halls of time? What are their most striking features? Do they bear scars of ancient battles, or eyes that glimmer with untold knowledge?
Imagine their attire and armor. Is it a suit of unbreakable mail, robes woven with the threads of magic, or leathers as silent as the night?
Consider their personality. Are they driven by honor, thirst for adventure, a quest for knowledge, or the shadows of their past?
Finally, picture them holding an item of great significance. Is it a weapon engraved with runes, a mystical amulet, or an ancient tome? This item will be a companion in their journey.
Let your words flow freely and paint the portrait of your character. Their story begins with your imagination. Here, in the realm of Hearth and Kin, every detail you conjure breathes life into their existence.
-

If we reach a point where we have enough information we can return a character description.
Please mark that section with "EMERGING FROM THE MISTS...\n---\n". 
The description should always start with the character name, like this "CHARACTER NAME: [name here]\n"
Then it should be followed by "CHARCTER RACE: [race here]\n".
Then it should be followed by "CHARCTER CLASS: [class here]\n".
Then by "CHARACTER DESCRIPTION: ", and end the final description with "---". 
Please provide a detailed description of everything we know about the character. 
This information will be used to generate an avatar as well as for the rest of the campaign.

Conversation with player so far:
{chat_history}
User input: {input}

"""
# parsed_system_prompt = prompt_narrator.format(character_data=character_data, location=location, goal=goal)
parsed_system_prompt = prompt_narrator

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=parsed_system_prompt),  # The persistent system prompt
        MessagesPlaceholder(variable_name='chat_history'),  # Where the memory will be stored.
        HumanMessagePromptTemplate.from_template('{input}'),  # Where the human input will injected
    ]
)
# print('Prompt is: ' + str(prompt))

memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

llm = ChatOpenAI(
    model_name='gpt-4o',
    # max_tokens=max_length,
    temperature=0.75,
)
chat_llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)


def gpt_character_creator(input: str, chain: LLMChain) -> str:
    message_and_character_data = input  # TODO: get this from db + '(Character Data: ' + session.get('character_data') + ')' + '(Location: ' + session.get('location') + ')' + '(Current Goal: ' + session.get('goal') + ')'
    print('[Character Creator] Input is: ' + message_and_character_data)
    output = chain.predict(input=message_and_character_data)
    print('[Character Creator] Output is: ' + output)
    return output

def initialize_character_stats(user_id: int, name: str, description: str, portrait_path: str, char_race: str, char_class: str):
    # Initialize and randomize character stats
    character_stats = {
        'stat_str': random.randint(1, 20),
        'stat_dex': random.randint(1, 20),
        'stat_con': random.randint(1, 20),
        'stat_int': random.randint(1, 20),
        'stat_wis': random.randint(1, 20),
        'stat_cha': random.randint(1, 20),
        'description': description,
        'character_name': name,
        'character_race': char_race,
        'character_class': char_class,
        'portrait_path': portrait_path
    }
    return character_stats

@router.post('/charactermessage')
async def generate_character_message(message: CharacterCreateMessage, response: Response):
    try:
        logger.debug(f'[MESSAGE] {message.message = }')
        narrator_reply = gpt_character_creator(input=message.message, chain=chat_llm_chain)
        
        final_character_creation_key = "EMERGING FROM THE MISTS..."
        portrait_path = None
        character_description = None
        character_data = None
        
        if final_character_creation_key in narrator_reply:
            character_name = re.search(r"CHARACTER NAME: (.+?)\n", narrator_reply).group(1)
            character_race = re.search(r"CHARACTER RACE: (.+?)\n", narrator_reply).group(1)
            character_class = re.search(r"CHARACTER CLASS: (.+?)\n", narrator_reply).group(1)
            character_description_match = re.search(r"CHARACTER DESCRIPTION:(.+?)\n---", narrator_reply, re.DOTALL)
            character_description = character_description_match.group(1).strip() if character_description_match else None
            
            logger.debug(f'[CREATION IMAGE] {character_description}')
            # Will send to dalle3 and obtain image
            portrait_url = imagery.generate(narrator_reply)
            _, portrait_path = await imagery.store(portrait_url, type='character')
            logger.debug(f'[MESSAGE] {portrait_path = }')
            
            character_data = initialize_character_stats(0, character_name, character_description, portrait_path, character_race, character_class)
        
        response.status_code = status.HTTP_201_CREATED
    except Exception as e:
        logger.error(f'[CREATION MESSAGE] {e}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'error': f'An error occurred while generating the response: {e}'}
    return {
            'message': 'Narrator: ' + narrator_reply,
            'image': portrait_path,
            'description': character_description,
            'character_data': character_data,
            'status': 'success'
    }

@router.post('/createcharacter', status_code=201, response_model=CharacterRead)
# async def create_character(*, character_stats: CharacterCreate, session: Session = Depends(get_session)):
async def create_character(character_stats: CharacterCreate, session: Session = Depends(get_session)):
    try:
        new_character = Character.model_validate(character_stats)
        session.add(new_character)
        session.commit()
        session.refresh(new_character)
        logger.debug(f'[CREATECHARACTER] New character created with ID: {new_character.character_id}')
        return new_character
    except ValidationError as ve:
        logger.error(f'[CREATECHARACTER] Validation error: {ve.json()}')
        raise HTTPException(status_code=422, detail=ve.errors())
    except Exception as e:
        logger.error(f'[CREATECHARACTER] Failed to create character: {e}')
        raise HTTPException(status_code=500, detail=str(e))