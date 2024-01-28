from langchain.utilities.dalle_image_generator import DallEAPIWrapper
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import httpx
from PIL import Image
from io import BytesIO
import base64
from ..core.config import logger


def generate_image(prompt_text):
    llm = ChatOpenAI(model_name='gpt-3.5-turbo')  # type: ignore
    prompt_gpt_helper = PromptTemplate(
        input_variables=['prompt_text'],
        template="""
        You are a virtual D&D scene prompt generator. 
        You will be given the latest narrator text from a cozy fantasy story that is currently developing.
        You must build a short prompt to generate an image based on the text. (no more than 100 tokens)
        Return it as "Scene Summary:".
        ---
        Here is the narration text:
        {prompt_text}
        """,
    )
    summary = LLMChain(llm=llm, prompt=prompt_gpt_helper).run(prompt_text=prompt_text)
    logger.debug('[GEN IMAGE]: ' + summary)
    image_url = ''
    prompt_dalle = (
        """
        You will be given a summary of a D&D story scene and you must build an image based on it.
        The illustration should mimic the style of a graphic novel, with bold and precise linework and a color palette of vibrant highlights. 
        The scene should feel alive and dynamic, yet cozy and intimate, capturing the essence of a fantasy adventure just about to unfold.
        Use a warm, cozy, fantasy style. Make it cinematic. Avoid text.
        Here is the scene description:
        """
        + summary
    )
    try:
        image_url = DallEAPIWrapper(model='dall-e-3', size='1024x1024').run(prompt_dalle)  # type: ignore
    except Exception as e:
        logger.debug('[GEN IMAGE] Image generation failed: ' + repr(e))
        image_url = '[NO_IMAGE]'
    return image_url


async def store_image(image_url: str, type: str) -> str:
    if type == 'story':
        # obtain image from url
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
        img = Image.open(BytesIO(response.content))
        # define path to save image
        visual_id = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
        dir_path = os.path.join('data', 'visuals', visual_id)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, 'image.jpg')
        img.save(file_path)
        return file_path
    elif type== 'character':
        # obtain image from url
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
        img = Image.open(BytesIO(response.content))
        # define path to save image
        visual_id = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
        # dir_path = os.path.join('data', 'characters', visual_id)
        dir_path = os.path.join('src', 'www', 'static', 'characters', visual_id)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, 'character.jpg')
        img.save(file_path)
        serve_image_path = file_path.replace('src/www/', '')
        return serve_image_path 
    else:
        error = 'Invalid store image type. Can only store `character` or `story` images'
        return error
    
