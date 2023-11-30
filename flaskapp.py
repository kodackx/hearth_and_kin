from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import pprint
import os
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from narrator import obtain_audio
from narrator import send_audio
from imagery import generate_image
from imagery import obtain_image_from_url
import random
import bcrypt

#read OPENAI_API_KEY from .env file
from dotenv import load_dotenv
load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'db', 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

with app.app_context():
    db.create_all()

# In-memory data structures for simplicity
users = {}  # {username: password}
game_rooms = {}  # {room_id: {players: [], ...}}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    print('[REGISTER] Inside /register route')
    pprint.pprint(request.__dict__)
    data = request.get_json()
    print('[REGISTER] Received data:', data)
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Missing username or password'}), 400
    print('[REGISTER] Received data:' + str(data))
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first() is not None:
        print('[REGISTER] user already exists')
        return jsonify({'error': 'Username already exists. Please try a different one.'}), 400
        # return jsonify({'message': 'Username already exists'}), 400
    
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    
    users[username] = password
    return jsonify({'message': 'User registered successfully! Please log in now.'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user is not None and bcrypt.checkpw(password.encode('utf-8'), user.password):
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create_game', methods=['POST'])
def create_game():
    data = request.get_json()
    room_id = data.get('room_id')
    
    if room_id in game_rooms:
        return jsonify({'error': 'Room already exists'}), 400
    
    game_rooms[room_id] = {'players': []}
    return jsonify({'message': f'Game room {room_id} created successfully'}), 201

@socketio.on('join_game')
def handle_join_game(data):
    room_id = data.get('room_id')
    username = session.get('username')
    
    if room_id not in game_rooms:
        return {'error': 'Room does not exist'}
    
    game_rooms[room_id]['players'].append(username)
    socketio.emit('player_joined', {'username': username}, room=room_id)

@app.route('/new_story', methods=['POST'])
def new_story():
    keywords = request.get_json().get('keywords')
    print('[NEW STORY] Received seed:' + keywords)
    session['character_input'] = keywords
    # randomize user stats for the beginning
    stats = { 'STR': 10, 'DEX': 10, 'CON': 10, 'INT': 10, 'WIS': 10, 'CHA': 10 }
    stats['STR'] = random.randint(1, 5)
    stats['DEX'] = random.randint(1, 5)
    stats['CON'] = random.randint(1, 5)
    stats['INT'] = random.randint(1, 5)
    stats['WIS'] = random.randint(1, 5)
    stats['CHA'] = random.randint(1, 5)
    session['stats'] = stats
    print('[NEW STORY] Stats saved for session are: ' + str(stats))

    character_data_template = "Character info: {user_input}, Level: 1, STR: {str}, DEX: {dex}, CON: {con}, INT: {int}, WIS: {wis}, CHA: {cha}, Pet: [randomized a pet that matches the character's class]"
    character_data = character_data_template.format(user_input=session.get('character_input'), 
            str=stats['STR'], 
            dex=stats['DEX'], 
            con=stats['CON'], 
            int=stats['INT'], 
            wis=stats['WIS'], 
            cha=stats['CHA'])
    location = 'The town of Hearth'
    goal = 'Find a quest to embark on and a party to join'
    session['character_data'] = character_data
    session['location'] = location
    session['goal'] = goal
 
    return jsonify({'message': 'New game created successfully. (' + keywords + ')' }), 201

@app.route('/story')
def story():
    return render_template('story.html')

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

prompt_narrator = '''
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

'''
# parsed_system_prompt = prompt_narrator.format(character_data=character_data, location=location, goal=goal)
parsed_system_prompt = prompt_narrator

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=parsed_system_prompt
        ),  # The persistent system prompt
        MessagesPlaceholder(
            variable_name="chat_history"
        ),  # Where the memory will be stored.
        HumanMessagePromptTemplate.from_template(
            "{input}"
        ),  # Where the human input will injected
    ]
)
# print('Prompt is: ' + str(prompt))

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatOpenAI(model_name="gpt-4", 
                # max_tokens=max_length, 
                    temperature=0.5)
chat_llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)
def gpt_narrator(input: str, chain):
    message_and_character_data = input + '(Character Data: ' + session.get('character_data') + ')' + '(Location: ' + session.get('location') + ')' + '(Current Goal: ' + session.get('goal') + ')'
    print('[GPT Narrator] Input is: ' + message_and_character_data)
    output = chain.predict(input=message_and_character_data)
    print('[GPT Narrator] Output is: ' + output)
    return output

@app.route('/message', methods=['POST'])
def message_received():
    message = request.get_json().get('message')
    print('[MESSAGE] Received user message:' + message)
    # Will send to openai and obtain reply
    narrator_reply = gpt_narrator(input=message, chain=chat_llm_chain)
    # Will send to narrator and obtain audio
    audio_path = obtain_audio(narrator_reply)
    narrator_audio = send_audio(audio_path)
    # Will send to dalle3 and obtain image
    background_path = generate_image(narrator_reply)
    print('[MESSAGE] Background path is: ' + background_path)
    background_image = obtain_image_from_url(background_path)
    print('[MESSAGE] Background image is: ' + background_image)
    # Will send to user
    socketio.emit('new_message', {'message': 'Openai reply: '})
    return jsonify({'message': 'Narrator: ' + narrator_reply, 'audio': narrator_audio, 'image': background_path ,'status': 'success'}), 201

if __name__ == '__main__':
    socketio.run(app, debug=True)


    
    