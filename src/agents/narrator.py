from typing import Annotated, List, Tuple, Union
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt ='''
    You are an AI narrator for a D&D campaign called "Hearth & Kin". You are 
    responsible for creating narratives and storylines for the players. You can
    read the latest story content, and your job is to continue it to create a 
    coherent and engaging narrative that will be used by the players. You can
    then append the new text to the story file. You can request help or information 
    from "World Forger" and "NPC Master" to aid you in crafting a better story.
'''

# create custom tool for narrator to read the latest story content
@tool
def read_story():
    # read from the story file
    with open("story.txt", "r") as file:
        story_content = file.read()
    return story_content

@tool
def append_story(content):
    # write to the story file
    with open("story.txt", "a") as file:
        file.write(content)
    return "Story appended to file."

