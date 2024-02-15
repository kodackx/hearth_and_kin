from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from src.models.character import Character

from src.models.message import MessageBase, MessageRead
from src.core.config import logger

################
# OpenAI stuff #
################
# """Generates a story based on the input string.
#     Args:
#         input (str): The input string to use as the story seed.
#         max_length (int, optional): The maximum number of tokens to generate. Defaults to 50.
#         temperature (float, optional): The temperature to use for generation. Defaults to 0.7.
#     Returns:
#         str: The generated story.
#     """

prompt_narrator = """
You are the Narrator and game master for Hearth and Kin, a game inspired from Dungeons and Dragons.
You must guide the adventurers (users) through a story in the style of a tabletop roleplaying game. 
The adventurers will be able to make choices that affect the story, and you must react to their choices 
in a way that makes sense for the story. You are most inspired by Critical Role campaigns.
    
Please describe in detail the locations, characters, and events that the adventurers encounter. 

Always take into account the following variables:
- The adventurers' current location
- The adventurers' current goal
- The adventurers' current state, stats and skills as well as equipment
- The adventurers' current relationships with other characters
- The adventurers' current character sheet data

DO NOT take decisions on behalf of the characters or express how they're feeling. 
Don't make any statements about the mystery of the journey they're embarking on or if they feel ready for a new quest.
The story needs to move at a slow pace, and each NPC has their own interests, which might not always mean they're interested in what the player has to say.

Don't make it easy for the players! Faliure is welcome and, in fact, used as a learning tool.
If the players go fight some enemies, don't gloss over the fight, give the player an opportunity to make some choices during combat.

You have access to three audiofiles. When the location changes or the mood of the story feel free to use the following commands:
1. [SOUNDTRACK: ambiance.m4a]
2. [SOUNDTRACK: cozy_tavern.m4a]
3. [SOUNDTRACK: wilderness.m4a]

Story so far:
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


def initialize_chain(prompt: ChatPromptTemplate, message_history: list[MessageRead]) -> LLMChain:
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    for message in message_history:
        memory.chat_memory.add_user_message(message.message)
        memory.chat_memory.add_ai_message(message.narrator_reply)

    llm = ChatOpenAI(
        model_name='gpt-4-0125-preview',  # type: ignore
        # max_tokens=max_length,
        temperature=0.5,
    )
    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    return chat_llm_chain


def gpt_narrator(character: Character, message: MessageBase, chain: LLMChain) -> str:
    message_and_character_data = message.message
    
    if character.character_name:
        message_and_character_data += f'\n(Character Name: {character.character_name})'

    if character.description:
        message_and_character_data += f'\n(Character Data: {character.description})'

    if character.location:
        message_and_character_data += f'\n(Location: {character.location})'

    if character.goal:
        message_and_character_data += f'\n(Current Goal: {character.goal})'

    logger.debug('[GPT Narrator] Input is: ' + message_and_character_data)
    output = chain.predict(input=message_and_character_data)
    logger.debug(f'[GPT Narrator] {output = }')
    return output
