import os
import httpx
from io import BytesIO
from PIL import Image
from openai import AsyncOpenAI
from dotenv import load_dotenv
import asyncio
import os
import json
import base64

load_dotenv()

async_client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def get_image_from_DALL_E_3_API(user_prompt, image_dimension="1792x1024", image_quality="hd", model="dall-e-3", nb_final_image=1, response_format="b64_json"):
    response = await async_client.images.generate(
        model=model,
        prompt=user_prompt,
        size=image_dimension,
        quality=image_quality,
        n=nb_final_image,
        response_format=response_format,
    )

    # Assuming the response is a JSON object with the base64-encoded image
    # Adjust the following line based on the actual structure of the response
# Convert response to JSON
    image_data_json = json.loads(response.json())  # Adjust based on response structure

    # Print the JSON response to understand its structure but only the first 200 characters
    print(json.dumps(image_data_json, indent=2)[:200])

    # Extract base64 string correctly based on the JSON structure
    # Example: image_data_base64 = image_data_json['someKey']['nestedKey']
    image_data_base64 = image_data_json['data'][0]['b64_json']

    image_data = base64.b64decode(image_data_base64)

    # Open the image and save it to a file
    image = Image.open(BytesIO(image_data))
    file_path = f"media/images/img_{user_prompt[:50]}.png"

    # Ensure the directory exists or create it
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    image.save(file_path)
    return file_path


async def main_async():
    start_time = asyncio.get_event_loop().time()
    await asyncio.gather(
        get_image_from_DALL_E_3_API("Test prompt 1"),
        get_image_from_DALL_E_3_API("Test prompt 2"),
        get_image_from_DALL_E_3_API("Test prompt 3")
    )
    end_time = asyncio.get_event_loop().time()
    print(f"Asynchronous execution time: {end_time - start_time}")

if __name__ == "__main__":
    asyncio.run(main_async())