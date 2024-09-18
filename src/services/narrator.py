from functools import lru_cache
from src.models.character import Character
from src.models.user import User
from src.models.message import MessageBase
from src.models.story import Story
from src.core.config import logger
from src.models.utils import get_or_create_uuid
from ..models.enums import CharacterType, TextModel
from typing import Dict
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from ..services.prompts.core_prompt import core_prompt
from ..services.prompts.scenario_1 import scenario
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from ..core.database import get_session
from fastapi import HTTPException, Depends
from sqlmodel import Session
from uuid import uuid4

# Dictionary to store chains by story_id
chains: Dict[str, RunnableWithMessageHistory] = {}

helper_prompt = """

The story so far:

"""

prompt_narrator = core_prompt + scenario + helper_prompt
# parsed_system_prompt = prompt_narrator.format(character_data=character_data, location=location, goal=goal)
parsed_system_prompt = prompt_narrator

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=parsed_system_prompt),  # The persistent system prompt
        MessagesPlaceholder(variable_name='chat_history'),  # Where the memory will be stored.
        HumanMessagePromptTemplate.from_template('{input}'),  # Where the human input will injected
    ]
)

def initialize_or_get_runnable(prompt: ChatPromptTemplate, 
                               message_history: list[MessageBase], 
                               story_id: str, 
                               text_model: TextModel, 
                               api_key: str, 
                               session) -> RunnableWithMessageHistory:
    """
    Initialize the runnable with the given prompt, message history, story id, text model, and API key.
    """
    # Check if the chain already exists for this story id

    if not isinstance(session, Session):
        raise HTTPException(status_code=400, detail="[NARRATOR - initialize_or_get_runnable] Session is not a valid SQLModel Session")
    
    if story_id in chains:
        return chains[story_id]
    
    # Initialize the appropriate text model
    if text_model in [TextModel.gpto1, TextModel.gpt4o, TextModel.gpt]:
        chat_model = ChatOpenAI(model=text_model, temperature=0.7, api_key=api_key)
    elif text_model == TextModel.claude:
        chat_model = ChatAnthropic(model=text_model, temperature=0.7, api_key=api_key)
    elif text_model == TextModel.nvidia:
        chat_model = ChatNVIDIA(model=text_model, temperature=0.7, api_key=api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported text model: {text_model}")

    memory = ChatMessageHistory()
    narrator_messages_list = []
    concatenated_narrator_message = ''
    if message_history:
        for message in message_history:
            # finding a narrator messages does not warrant a dump into memory
            if message.character in {CharacterType.narrator, CharacterType.system}:
                narrator_messages_list.append(message.message)
            # user messages require no concatenation (they are always singular)
            # but they should trigger the dump of all narrator messages gathered in the chunk so far
            # and these should be dumped first
            elif message.character == CharacterType.player:
            # If there are accumulated narrator messages, add them to memory
                if narrator_messages_list:
                    for narrator_piece in narrator_messages_list:
                        concatenated_narrator_message += narrator_piece
                    if text_model == TextModel.nvidia:
                        memory.add_ai_message('assistant: ' + concatenated_narrator_message)
                        narrator_messages_list = []
                        logger.debug(' Added a big narrator message.')
                    else:
                        memory.add_ai_message(concatenated_narrator_message)
                        narrator_messages_list = []
                        logger.debug('Added a big narrator message.')
                # now add the user message we found
                if text_model == TextModel.nvidia:
                    memory.add_user_message('user: ' + message.message)
                else:
                    memory.add_user_message(message.message)       
        # Ensure any remaining narrator messages are added to memory
        if narrator_messages_list:
            for narrator_piece in narrator_messages_list:
                concatenated_narrator_message += narrator_piece
            if text_model == TextModel.nvidia:
                memory.add_ai_message('assistant: ' + concatenated_narrator_message)
            else:
                memory.add_ai_message(concatenated_narrator_message)
            logger.debug('Added remaining narrator messages.')
    else:
        logger.debug("No message history. Will start story from scratch.")

    chat_llm_chain = prompt | chat_model | StrOutputParser()
    run_id=get_or_create_uuid(story_id, session)
    logger.debug(f'[NARRATOR] Run ID: {run_id}')
    chain_with_message_history = RunnableWithMessageHistory(
        chat_llm_chain,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    ).with_config(run_id=run_id)

    # Store the chain in the dictionary
    chains[story_id] = chain_with_message_history
    logger.debug(f'[NARRATOR] Initialized or got runnable for story {story_id}')
    
    return chain_with_message_history

def get_chain(story_id: str) -> RunnableWithMessageHistory | None:
    """
    Get the chain for the given story id.
    """
    return chains.get(story_id)


def _gpt_narrator(character: Character, message: MessageBase, runnable: RunnableWithMessageHistory, runnable_uuid: str, text_model: TextModel, party_info: str = '') -> str:
    message_and_character_data = message.message
    
    if character.character_name:
        message_and_character_data += f'\n(SYSTEM NOTE - Character Name: {character.character_name})'

    if party_info:
        message_and_character_data += f'\n(SYSTEM NOTE - Party Info: {party_info})'
    
    if text_model == TextModel.nvidia:
       message_and_character_data = 'user: ' + message_and_character_data

    logger.debug('[GPT Narrator] Input is: ' + message_and_character_data)
    output = runnable.invoke({"input": message_and_character_data}, {"configurable": {"session_id": runnable_uuid}})
    logger.debug(f'[GPT Narrator] {output = }')
    return output

def generate_reply(character: Character, message: MessageBase, runnable: RunnableWithMessageHistory, runnable_uuid: str, text_model: TextModel, party_info: str = '') -> tuple[str, str | None]:
    narrator_reply = _gpt_narrator(character=character, message=message, runnable=runnable, runnable_uuid=runnable_uuid, party_info=party_info, text_model=text_model)
    # Remove "assistant: " prefix if present
    if narrator_reply.startswith(" assistant: "):
        narrator_reply = narrator_reply[len(" assistant: "):]
    if narrator_reply.startswith("assistant: "):
        narrator_reply = narrator_reply[len("assistant: "):]
    soundtrack_path = None
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
        # TODO: We shouldn't always have a soundtrack, so we should handle that case
    return narrator_reply, soundtrack_path

def validate_api_key(model: TextModel, api_key: str) -> None:
    llm = ChatOpenAI(model='gpt-4o', temperature=0.75, api_key=api_key)

    llm.invoke('Hello, world!')
