import os
import requests
from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_image_from_DALL_E_3_API(user_prompt, image_dimension="1792x1024", image_quality="hd", model="dall-e-3", nb_final_image=1):
    response = client.images.generate(
        model=model,
        prompt=user_prompt,
        size=image_dimension,
        quality=image_quality,
        n=nb_final_image,
    )

    image_url = response.data[0].url
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        file_path = f"media/images/img_{user_prompt[:50]}.png"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        image.save(file_path)
        return file_path
    return None

def main():
    start_time = time.time()
    for i, prompt in enumerate(["Test prompt 1", "Test prompt 2", "Test prompt 3"], start=1):
        file_path = get_image_from_DALL_E_3_API(prompt)
        print(file_path)
    end_time = time.time()
    print(f"Synchronous execution time: {end_time - start_time}")

if __name__ == "__main__":
    main()
