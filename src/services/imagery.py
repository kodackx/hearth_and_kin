from langchain.utilities.dalle_image_generator import DallEAPIWrapper
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import base64
from ..core.config import logger
from ..core import azure


def generate(prompt_text):
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


async def store(image_url: str, type: str) -> tuple[str,str]:
    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
    if type == 'character':
        path = f'img/characters/{unique_id}.jpg'
    elif type == 'story':
        path = f'img/stories/{unique_id}.jpg'
    azure_url = azure.store_public(remote_path=path, url = image_url)
    return unique_id, azure_url
