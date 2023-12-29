from fastapi import APIRouter, Response, status
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

from ..core.config import logger, GENERATE_IMAGE, GENERATE_AUDIO
from ..core.database import engine
from ..models.message import Message, MessageBase
from ..services import audio, imagery

router = APIRouter()

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

memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

llm = ChatOpenAI(
    model_name='gpt-4',
    # max_tokens=max_length,
    temperature=0.5,
)
chat_llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)


def gpt_narrator(input: str, chain: LLMChain) -> str:
    message_and_character_data = input  # TODO: get this from db + '(Character Data: ' + session.get('character_data') + ')' + '(Location: ' + session.get('location') + ')' + '(Current Goal: ' + session.get('goal') + ')'
    print('[GPT Narrator] Input is: ' + message_and_character_data)
    output = chain.predict(input=message_and_character_data)
    print('[GPT Narrator] Output is: ' + output)
    return output


@router.post('/message')
async def generate_message(message: MessageBase, response: Response):
    # TODO: move the openai/audio/narrator stuff to a message/orchestrator service instead
    audio_id = audio_path = background_path = background_image = None
    try:
        logger.debug(f'[MESSAGE] {message.message = }')
        # Will send to openai and obtain reply
        narrator_reply = gpt_narrator(input=message.message, chain=chat_llm_chain)

        if GENERATE_AUDIO:  # Will send to narrator and obtain audio
            audio_id, audio_path = audio.obtain_audio(narrator_reply)
            _ = await audio.store_audio(audio_id, audio_path)
            if GENERATE_IMAGE:  # Will send to dalle3 and obtain image
                background_path = imagery.generate_image(narrator_reply)
                logger.debug(f'[MESSAGE] {background_path = }')
                background_image = imagery.obtain_image_from_url(background_path)
                logger.debug(f'[MESSAGE] {background_image = }')
    except Exception as e:
        logger.error(f'[MESSAGE] {e}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'error': f'An error occurred while generating the response: {e}'}
    # Will send to user
    # TODO: Replace socketio.emit with the appropriate method to send data to the client
    # socketio.emit('new_message', {'message': 'Openai reply: '})
    with Session(engine) as session:
        new_message = Message(
            message=message.message, narrator_reply=narrator_reply, audio_path=audio_path, image_path=background_path
        )
        logger.debug(f'{new_message = }')
        session.add(new_message)
        session.commit()
        session.refresh(new_message)
        response.status_code = status.HTTP_201_CREATED
        return new_message
