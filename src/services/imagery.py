import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import os
import base64
import httpx
from PIL import Image
from io import BytesIO

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from ..core.config import logger
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

text_models = {
    'gpt': ChatOpenAI(model_name='gpt-4o'),
    'nvidia': ChatNVIDIA(model_name='meta/llama3-8b-instruct', temperature=0.75),
}

image_models = {
    'dalle3': DallEAPIWrapper(model='dall-e-3', size='1024x1024'),
}



def _generate_blocking(prompt_text: str, text_model: str, image_model: str) -> str:
    prompt_gpt_helper = PromptTemplate(
        input_variables=['prompt_text'],
        template="""
        You will be given the latest narrator text from a cozy fantasy story that is currently developing.
        You must build a short prompt to generate an image that will be sent to Dall-e3. 
        The prompt should be expressed as image captions, just like they are found on the internet. 
        You must build a short prompt to generate an image that will be sent to Dall-e3. 
        The prompt should be expressed as image captions, just like they are found on the internet. 
        Return it as "Scene Summary:".
        ---
        Here is the narration text:
        {prompt_text}
        """,
    )
    chain = prompt_gpt_helper | text_models[text_model] | StrOutputParser()
    result = chain.invoke({'prompt_text': prompt_text})
    logger.debug('[GEN IMAGE]: ' + result)
    image_url = ''
    prompt_dalle = (
        """
        You will be given a summary of a D&D story scene and you must build an image based on it.
        The illustration should mimic the style of a graphic novel, with bold and precise linework and a color palette of vibrant highlights. 
        The scene should feel alive and dynamic, yet cozy and intimate, capturing the essence of a fantasy adventure just about to unfold.
        Use a warm, cozy, fantasy style. Make it cinematic. No text.
        Here is the scene description:
        """
        + result
    )
    if image_model == 'dalle3':
        try:
            image_url = image_models[image_model].run(prompt_dalle)  # type: ignore
        except Exception as e:
            logger.debug('[GEN IMAGE] Image generation failed: ' + repr(e))
            image_url = None
    else:
        image_url = None
    return image_url


async def _store(image_url: str, type: str, filename: Optional[str] = None) -> tuple[str,str]:
    """
    Store an image from an URL and return the url to the stored file
    """
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
        return visual_id, file_path
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
        return visual_id, serve_image_path 
    else:
        error = 'Invalid store image type. Can only store `character` or `story` images'
        return '0', error

async def _generate(prompt_text: str, text_model: str, image_model: str) -> str:
    """
    Needed to not let the image generation block the event loop
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, _generate_blocking, prompt_text, text_model, image_model)
    return result


async def generate_image(prompt: str, type: str, text_model: str, image_model: str) -> str:
    image_url = await _generate(prompt, text_model, image_model)
    image_path = 'static/img/login1.png'
    if image_url is not None:
        _, image_path = await _store(image_url=image_url, type=type)
    return image_path