from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import httpx
from PIL import Image
from io import BytesIO
import base64
from ..core.config import logger
import asyncio
import base64
import requests
import os


async def generate_image(prompt_text: str, model: str):
    '''
    Generate an image based on a prompt using the specified model
    The models can be 'dalle3' or 'stability'
    '''
    loop = asyncio.get_event_loop()
    llm = ChatOpenAI(model_name='gpt-3.5-turbo')  # type: ignore
    prompt_gpt_helper = PromptTemplate(
        input_variables=['prompt_text'],
        template="""
        You are a virtual D&D scene prompt generator. 
        You will be given the latest narrator text from a cozy fantasy story that is currently developing.
        You must build a short prompt to generate an image based on the text.
        
        MAIN ASK: Describe the characters in the scene and the location. Be as concise as possible.
        Express them as captions (example: "An oil painting of a panda by Leonardo da Vinci and Frederic Edwin Church, highly-detailed, dramatic lighting")
        Return it as "Scene Description:".
        ---
        Here is the narration text:
        {prompt_text}
        """,
    )
    scene_description = LLMChain(llm=llm, prompt=prompt_gpt_helper).run(prompt_text=prompt_text)
    logger.debug('[GEN IMAGE]: ' + scene_description)
    image_url = ''
    prompt_dalle = f'{scene_description} Warm, fantasy style with no text.'
    try:
        if model == 'dalle3':
            image_url = DallEAPIWrapper(model='dall-e-3', size='1024x1024').run(prompt_dalle)
        elif model == 'stability':
            image_url = stability_ai(prompt_dalle)
    except Exception as e:
        logger.debug('[GEN IMAGE] Image generation failed: ' + repr(e))
        image_url = '[NO_IMAGE]'
    return image_url


async def store_image(image_url: str, type: str, model: str) -> str:
    # using the stability model will already save the file and return the path
    if model == 'stability':
        return image_url
    else:
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
    
def stability_ai(prompt: str):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    body = {
    "steps": 40,
    "width":  1152,
    "height": 896,
    "seed": 0,
    "cfg_scale": 5,
    "samples": 1,
    "text_prompts": [
        {
        "text": prompt,
        "weight": 1
        },
        {
        "text": "blurry, bad",
        "weight": -1
        }
    ],
    }

    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-Kob2hHG0coivg8f9ids8Giyv8yYuFqLVSoz6ZC0xVHdaZUPZ",
    }

    response = requests.post(
        url,
        headers=headers,
        json=body,
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    output_path = os.path.join('data', 'visuals', 'stability')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # make sure the out directory exists
    # if not os.path.exists("./out"):
    #     os.makedirs("./out")

    for i, image in enumerate(data["artifacts"]):
        # print("[GEN IMAGE]: Stability AI artifacts: " +  str(i) + "/" + str(image))
        image_path = f'{output_path}/{image["seed"]}.png'
        # print("[GEN IMAGE]: Stability AI image path: " + image_path)
        with open(f'{output_path}/{image["seed"]}.png', "wb") as f:
            f.write(base64.b64decode(image["base64"]))
    
    return image_path

