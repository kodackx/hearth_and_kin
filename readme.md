# Flask Application

This is a Flask application that uses several libraries and APIs to provide a chat interface with various features.

## Libraries and APIs Used

- Flask: A micro web framework written in Python.
- Flask-SocketIO: Flask extension for SocketIO, a real-time communication library.
- Flask-SQLAlchemy: Flask extension for SQLAlchemy, an SQL toolkit and ORM.
- OpenAI: An API for accessing OpenAI's artificial intelligence models.
- dotenv: A library to read environment variables from a .env file.

## Key Features

- Real-time communication: This application uses Flask-SocketIO to provide real-time communication.
- Database: This application uses Flask-SQLAlchemy to manage a SQLite database.
- AI Integration: This application uses OpenAI's API to integrate AI capabilities.
- Environment Variables: This application uses dotenv to manage environment variables.

## Code Structure

The main application is created as a Flask object. A SocketIO object is also created for real-time communication. The application is configured to use a SQLite database located at 'db/test.db'.

A User model is defined for the database with the following fields:
- id: A unique identifier for each user.
- username: A unique username for each user.
- password: The user's password.

## Environment Variables

The application uses the following environment variables:
- OPENAI_API_KEY: The API key for OpenAI.
- ELEVENLABS_API_KEY: The API key for ElevenLabs.
- ELEVENLABS_VOICE_ID: The voice ID for ElevenLabs.

## Development

Install [pyenv](https://github.com/pyenv/pyenv). When you enter the directory, it will recognize which python version should be used (`.python-version file`) and use it automatically.

```bash
cd hearth_and_kin
```

Connect poetry to the proper version of python

```bash
poetry env use $(which python)
```

Install dependencies locally

```bash
poetry install
```

Run tests (pytest)

```bash
make test
```