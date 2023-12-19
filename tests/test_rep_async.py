import asyncio
import replicate
import httpx
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()

async def get_video_from_Replicate_API(image_path, video_length="25_frames_with_svd_xt"):
    url = await replicate.async_run(
        "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
        input={"input_image": open(image_path, "rb"), "video_length": video_length}
    )

    # Generate a unique output path based on the input image name
    base_name = os.path.basename(image_path)
    output_path = f"media/videos/video_{base_name[:-4]}.mp4"
    #wait for the video to be generated
    await asyncio.sleep(100)
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as video_file:
                async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                    video_file.write(chunk)
            return output_path
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
            return None

async def main_async():
    start_time = asyncio.get_event_loop().time()

    image_paths = [
        "media/images/img_A diverse crew of spacefarers is intently focused .png",
        "media/images/img_A diverse crew of spacefarers is intently focused .png",
        "media/images/img_A diverse crew of spacefarers is intently focused .png",
    ]

    tasks = [get_video_from_Replicate_API(image_path) for image_path in image_paths]
    video_paths = await asyncio.gather(*tasks)

    for video_path in video_paths:
        print(video_path)

    end_time = asyncio.get_event_loop().time()
    print(f"Asynchronous execution time: {end_time - start_time} seconds")

if __name__ == "__main__":
    asyncio.run(main_async())
