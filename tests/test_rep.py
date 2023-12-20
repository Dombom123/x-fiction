import replicate
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

def get_video_from_Replicate_API(image_path, video_length="25_frames_with_svd_xt"):
    """
    Generate a video from an image using the Replicate API.

    :param image_path: Path to the image to use as input.
    :param video_length: Length of the video to generate.
    :return: Path to the generated video.
    """
    url = replicate.run(
        "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
        input={"input_image": open(image_path, "rb"), "video_length": video_length}
    )
    # download the video from the URL

    response = requests.get(url)
    if response.status_code == 200:
        # Open the video and save it to a file
        video = Image.open(BytesIO(response.content))
        file_path = f"videos/video_{image_path[7:-4]}.mp4"  # Limiting prompt length to avoid too long file names
        video.save(file_path)
        return file_path


def main():
    image_path = "media/images/img_An elaborately dressed demon with sharp attire and.png"
    video_path = get_video_from_Replicate_API(image_path)
    print(video_path)

if __name__ == "__main__":
    main()