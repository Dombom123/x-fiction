import os
from openai import OpenAI
import json
import requests
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
import replicate
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import utils.download_from_url as download
from pathlib import Path
# Load environment variables from .env file
load_dotenv()
client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

def generate_story(story_prompt):
    """
    Generate a story with title, voiceover, and image prompts in JSON format.

    :param api_key: OpenAI API key.
    :param story_prompt: The initial prompt for the story.
    :return: JSON formatted story with title, voiceover, and image prompts.
    """


    
    # get system prompt from txt file
    systemprompt = open("systemprompt.txt", "r")
    systemprompt = systemprompt.read()

    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": systemprompt
                },
                {
                    "role": "user",
                    "content": story_prompt
                }
            ],
            response_format={ "type": "json_object" },
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def generate_voiceover(voiceover_text):
    """
    Generate a voiceover from text using the OpenAI API.
    """

    speech_file_path = Path(__file__).parent / f"media/voiceover/speech{voiceover_text[:25]}.mp3"
    response = client.audio.speech.create(
    model="tts-1-hd",
    voice="onyx",
    input=voiceover_text
    )

    response.stream_to_file(speech_file_path)
    path_str = str(speech_file_path)
    return path_str

def get_image_from_DALL_E_3_API(user_prompt, image_dimension="1792x1024", image_quality="hd", model="dall-e-3", nb_final_image=1):
    response = client.images.generate(
        model=model,
        prompt=user_prompt,
        size=image_dimension,
        quality=image_quality,
        n=nb_final_image,
    )

    image_url = response.data[0].url

    # Download the image from the URL
    response = requests.get(image_url)
    if response.status_code == 200:
        # Open the image and save it to a file
        image = Image.open(BytesIO(response.content))
        file_path = f"media/images/img_{user_prompt[:50]}.png"  # Limiting prompt length to avoid too long file names
        image.save(file_path)
        return file_path

    return None

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
    download.download_video_from_url(url, f"media/clips/video_{image_path[7:-4]}.mp4")

def combine_videos_and_audio(video_paths, audio_path, output_path):
    """
    Combine multiple videos into one and add an audio track using MoviePy.

    :param video_paths: A list of paths to the video files.
    :param audio_path: Path to the audio file.
    :param output_path: Path where the output video will be saved.
    """
    # Load all the video clips
    video_clips = [VideoFileClip(path) for path in video_paths]

    # Concatenate the video clips
    final_clip = concatenate_videoclips(video_clips)

    # Load the audio file
    audio_clip = AudioFileClip(audio_path)

    # Set the audio of the concatenated clip as the audio clip
    final_clip = final_clip.set_audio(audio_clip)

    # Write the result to the output file
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # Close the clips
    final_clip.close()
    for clip in video_clips:
        clip.close()
    audio_clip.close()

    return output_path

# Example usage
def main():
    story_prompt = "Funny Scene from a Sitcom about the Devil's Job as a Lawyer"
    story_json = generate_story(story_prompt)
    print(story_json)
    story_json_dict = json.loads(story_json)
    # Extract title
    title = story_json_dict["title"]
    # Extract voiceover text
    voiceover_text = story_json_dict["voiceover_text"]
    speech = generate_voiceover(voiceover_text)
    video_paths = []    

    # Extract image prompts from each clip
    prompts = []
    visual_style = story_json_dict["visual_style"]
    if "clips" in story_json_dict:
        for clip_value in story_json_dict["clips"].items():
            if "image_prompt" in clip_value:
                prompts.append(f'{clip_value["image_prompt"]} + {visual_style}')
                
                

    # Now 'prompts' contains all the image prompts
    for i, prompt in prompts:
        print(f"Generating image number {i} for prompt: {prompt}")
        img_path = get_image_from_DALL_E_3_API(prompt)
        print(f"Generating video number {i}")
        get_video_from_Replicate_API(img_path)
        video_paths.append(f"media/clips/video_img_{i}.mp4")
        i += 1
    # Combine all the videos and speech into one
    output_video_path = f"media/videos/{title}.mp4"
    combine_videos_and_audio(video_paths, speech, output_video_path)

    print(f"Combined video and audio saved to {output_video_path}")
            

if __name__ == "__main__":
    main()