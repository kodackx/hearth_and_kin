
from openai import AuthenticationError
from src.models.character import Character
from src.models.user import User
from src.models.message import MessageBase
from src.models.story import Story
from src.core.config import logger
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
from ..models.utils import get_text_models
from ..core.database import get_session
from fastapi import HTTPException

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
# logger.info('Prompt is: ' + str(prompt))

def initialize_chain(prompt: ChatPromptTemplate, message_history: list[MessageBase], story_id: str) -> RunnableWithMessageHistory:
    #memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    session = get_session()
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(404, 'Story not found')
    
    text_model = story.genai_text_model
    party_lead_user_id = story.party_lead

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
                    if text_model == TextModel.nvidia_llama:
                        memory.add_ai_message('assistant: ' + concatenated_narrator_message)
                        narrator_messages_list = []
                        logger.debug(' Added a big narrator message.')
                    else:
                        memory.add_ai_message(concatenated_narrator_message)
                        narrator_messages_list = []
                        logger.debug('Added a big narrator message.')
                # now add the user message we found
                if text_model == TextModel.nvidia_llama:
                    memory.add_user_message('user: ' + message.message)
                else:
                    memory.add_user_message(message.message)       
        # Ensure any remaining narrator messages are added to memory
        if narrator_messages_list:
            for narrator_piece in narrator_messages_list:
                concatenated_narrator_message += narrator_piece
            if text_model == TextModel.nvidia_llama:
                memory.add_ai_message('assistant: ' + concatenated_narrator_message)
            else:
                memory.add_ai_message(concatenated_narrator_message)
            logger.debug('Added remaining narrator messages.')
    else:
        logger.debug("No message history. Will start story from scratch.")
    
    models = get_text_models(text_model, party_lead_user_id)

    chat_llm_chain = prompt | models[text_model] | StrOutputParser()
    chain_with_message_history = RunnableWithMessageHistory(
        chat_llm_chain,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    # Store the chain in the dictionary
    chains[story_id] = chain_with_message_history

    return chain_with_message_history

def get_chain(story_id: str) -> RunnableWithMessageHistory | None:
    return chains.get(story_id)


def _gpt_narrator(character: Character, message: MessageBase, chain: RunnableWithMessageHistory, text_model: TextModel, party_info: str = '') -> str:
    message_and_character_data = message.message
    
    if character.character_name:
        message_and_character_data += f'\n(SYSTEM NOTE - Character Name: {character.character_name})'

    if party_info:
        message_and_character_data += f'\n(SYSTEM NOTE - Party Info: {party_info})'
    
    if text_model == TextModel.nvidia_llama:
       message_and_character_data = 'user: ' + message_and_character_data

    logger.debug('[GPT Narrator] Input is: ' + message_and_character_data)
    output = chain.invoke({'input': message_and_character_data}, {"configurable": {"session_id": message.story_id}})
    logger.debug(f'[GPT Narrator] {output = }')
    return output

def generate_reply(character: Character, message: MessageBase, chain: RunnableWithMessageHistory, text_model: TextModel, party_info: str = '') -> tuple[str, str | None]:
    narrator_reply = _gpt_narrator(character=character, message=message, chain=chain, party_info=party_info, text_model=text_model)
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
    return narrator_reply, soundtrack_path

def validate_api_key(model: TextModel, api_key: str) -> None:
    llm = ChatOpenAI(model='gpt-4o', temperature=0.75, api_key=api_key)

    llm.invoke('Hello, world!')
