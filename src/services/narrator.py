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
You are the Narrator for Hearth and Kin, a game inspired from Dungeons and Dragons.
You must guide the adventurers (users) through a story in the style of a tabletop roleplaying game. 
The adventurers will be able to make choices that affect the story, and you must react to their choices 
in a way that makes sense for the story. 
    
Please describe in detail the locations, characters, and events that the adventurers encounter. 

Always take into account the following variables:
- The adventurers' current location
- The adventurers' current goal
- The adventurers' current state, stats and skills as well as equipment
- The adventurers' current relationships with other characters
- The adventurers' current character sheet data

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
        model_name='gpt-4',  # type: ignore
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

    if character.user_description:
        message_and_character_data += f'\n(Character Data: {character.user_description})'

    if character.location:
        message_and_character_data += f'\n(Location: {character.location})'

    if character.goal:
        message_and_character_data += f'\n(Current Goal: {character.goal})'

    logger.debug('[GPT Narrator] Input is: ' + message_and_character_data)
    output = chain.predict(input=message_and_character_data)
    logger.debug(f'[GPT Narrator] {output = }')
    return output
