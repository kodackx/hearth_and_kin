from fastapi import FastAPI, Request, Response, status
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from .services import narrator, imagery
from .core.database import create_db_and_tables
from src.models.main import UserCreate, UserLogin, CreateGameRequest, NewStoryRequest, MessageRequest
import random
import bcrypt
import requests
import os
from .core.config import logger
from .core import database

# read OPENAI_API_KEY from .env file
from dotenv import load_dotenv

load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

app = FastAPI()
app.mount('/static', StaticFiles(directory=Path('src/www/static')), name='static')


@app.router.on_startup.append
async def on_startup():
    create_db_and_tables()


@app.get('/')
async def home(request: Request):
    return Response(content=open('src/www/templates/index.html', 'r').read(), media_type='text/html')


@app.post('/user')
async def create_user(user: UserCreate, response: Response):
    logger.debug(f'CREATE_USER: {user = }')
    db_user = database.get_user(user.username)
    if db_user is not None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Username already exists. Please try a different one.'}

    database.create_user(user)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'User registered successfully! Please log in now.'}


@app.post('/login')
async def login(user: UserLogin, response: Response):
    db_user = database.get_user(user.username)
    if db_user is not None and bcrypt.checkpw(user.password.encode(), db_user.password.encode()[8:]):
        response.status_code = status.HTTP_200_OK
        return {'message': 'Login successful'}

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {'error': 'Invalid credentials'}


@app.get('/dashboard')
async def dashboard(request: Request) -> Response:
    return Response(content=open('src/www/templates/dashboard.html', 'r').read(), media_type='text/html')


@app.post('/create_game')
async def create_game(request: CreateGameRequest, response: Response):
    room_id = request.room_id

    if room_id in game_rooms:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Room already exists'}

    game_rooms[room_id] = {'players': []}
    response.status_code = status.HTTP_201_CREATED
    return {'message': f'Game room {room_id} created successfully'}


# TODO: figure out how this works in fastapi
"""
@socketio.on('join_game')
def handle_join_game(data):
    room_id = data.get('room_id')
    username = session.get('username')
    
    if room_id not in game_rooms:
        return {'error': 'Room does not exist'}
    
    game_rooms[room_id]['players'].append(username)
    socketio.emit('player_joined', {'username': username}, room=room_id)
"""


@app.post('/new_story')
def new_story(request_data: NewStoryRequest, response: Response):
    keywords = request_data.keywords
    logger.debug('NEW_STORY: {keywords = }')
    # Randomize user stats for the beginning
    stats = {
        'STR': random.randint(1, 5),
        'DEX': random.randint(1, 5),
        'CON': random.randint(1, 5),
        'INT': random.randint(1, 5),
        'WIS': random.randint(1, 5),
        'CHA': random.randint(1, 5),
    }
    character_data = f"Character info: {keywords}, Level: 1, STR: {stats['STR']}, DEX: {stats['DEX']}, CON: {stats['CON']}, INT: {stats['INT']}, WIS: {stats['WIS']}, CHA: {stats['CHA']}, Pet: [randomized a pet that matches the character's class]"
    location = 'The town of Hearth'
    goal = 'Find a quest to embark on and a party to join'
    # TODO: store this is DB or in browser
    # session['character_data'] = character_data
    # session['location'] = location
    # session['goal'] = goal
    response.status_code = status.HTTP_201_CREATED
    return {'message': f'New game created successfully. ({keywords})'}


@app.get('/story')
async def story(request: Request):
    return Response(content=open('src/www/templates/story.html', 'r').read(), media_type='text/html')


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


def gpt_narrator(input: str, chain):
    message_and_character_data = (
        input
        + '(Character Data: '
        + session.get('character_data')
        + ')'
        + '(Location: '
        + session.get('location')
        + ')'
        + '(Current Goal: '
        + session.get('goal')
        + ')'
    )
    logger.debug('[GPT Narrator] Input is: ' + message_and_character_data)
    output = chain.predict(input=message_and_character_data)
    logger.debug(f'[GPT Narrator] {output = }')
    return output


@app.post('/message')
def message_received(request_data: MessageRequest, response: Response):
    message = request_data.message
    logger.debug(f'[MESSAGE] {message = }')
    # Will send to openai and obtain reply
    narrator_reply = requests.post('http://openai-api-url', json={'input': message}).json()
    # Will send to narrator and obtain audio
    audio_path = narrator.obtain_audio(narrator_reply)
    narrator_audio = narrator.send_audio(audio_path)
    # Will send to dalle3 and obtain image
    background_path = imagery.generate_image(narrator_reply)
    logger.debug(f'[MESSAGE] {background_path = }')
    background_image = imagery.obtain_image_from_url(background_path)
    logger.debug(f'[MESSAGE] {background_image = }')
    # Will send to user
    # TODO: Replace socketio.emit with the appropriate method to send data to the client
    # socketio.emit('new_message', {'message': 'Openai reply: '})
    response.status_code = status.HTTP_201_CREATED
    return {
        'message': 'Narrator: ' + narrator_reply,
        'audio': narrator_audio,
        'image': background_path,
        'status': 'success',
    }
