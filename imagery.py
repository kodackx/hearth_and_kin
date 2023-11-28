from langchain.utilities.dalle_image_generator import DallEAPIWrapper
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
import requests
from PIL import Image
from io import BytesIO
import base64


def generate_image(prompt_text):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    prompt = PromptTemplate(
        input_variables=["prompt_text"],
        template='''
        You are a virtual D&D scene generator. 
        You will be given the latest narrator text from a story that is currently developing.
        You must build a short prompt to generate an image based on the text.(no more than 100 tokens)
        Return it as "Scene Summary:".
        ---
        Here is the narration text:
        {prompt_text}
        '''
    )
    summary = LLMChain(llm=llm, prompt=prompt).run(prompt_text=prompt_text)
    print('[GEN IMAGE]: ' + summary)
    image_url = ""
    prompt_text_adjusted = '''
        You are a virtual D&D scene generator. 
        The narrator is currently developing a story.
        You will be given a summary of a scene and you must build an image based on it.
        Use a fantasy sketch style and make it look like a D&D scene.
        ''' + summary
    try:
        image_url = DallEAPIWrapper(model="dall-e-3", size="1024x1024").run(prompt_text_adjusted)
    except Exception as e:
        print('[GEN IMAGE] Image generation failed: ' + repr(e))
        image_url = '[NO_IMAGE]'
    return image_url

def obtain_image_from_url(image_url):
    # obtain image from url
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    # define path to save image
    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("static")
    os.makedirs(dir_path, exist_ok=True)
    filename = unique_id + ".jpg"
    file_path = os.path.join(dir_path, filename)
    # save image to local file for debugging
    img.save(file_path) 
    return file_path
