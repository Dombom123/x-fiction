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
import streamlit as st


# Load environment variables from .env file
load_dotenv()
client = OpenAI(
        # This is the default and can be omitted
        api_key=st.secrets["OPENAI_API_KEY"],
    )

def generate_example_prompt():
    """
    Generate an example prompt from the OpenAI API.
    :param api_key: OpenAI API key.
    :return: JSON formatted three example prompts
    """
    # get system prompt from txt file
    systemprompt = open("systemprompt_gen_examples.txt", "r")
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
                    "content": "Generate three very short example prompts for the Dreammachine"
                }
            ],
            response_format={ "type": "json_object" },
            temperature=1.0,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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
    # make sure the directory exists
    os.makedirs("media/voiceover", exist_ok=True)
    speech_file_path = Path(__file__).parent / f"media/voiceover/speech_{voiceover_text[:25]}.mp3"
    response = client.audio.speech.create(
    model="tts-1-hd",
    voice="onyx",
    input=voiceover_text
    )

    response.stream_to_file(speech_file_path)
    path_str = str(speech_file_path)
    return path_str

def get_image_from_DALL_E_3_API(user_prompt, image_dimension="1024x1024", image_quality="standard", model="dall-e-3", nb_final_image=1, style="vivid"):
    response = client.images.generate(
        model=model,
        prompt=user_prompt,
        size=image_dimension,
        quality=image_quality,
        n=nb_final_image,
        style=style,
    )

    image_url = response.data[0].url

    # Download the image from the URL
    response = requests.get(image_url)
    if response.status_code == 200:
        # Open the image and save it to a file
        image = Image.open(BytesIO(response.content))
        file_path = f"media/images/img_{user_prompt[:50]}.png"  # Limiting prompt length to avoid too long file names
        os.makedirs("media/images", exist_ok=True)
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
    file_path = f"media/clips/clip_{image_path[17:-4]}.mp4"
    os.makedirs("media/clips", exist_ok=True)
    download.download_video_from_url(url, file_path)
    
    return file_path

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

    os.makedirs("media/videos", exist_ok=True)

    # Write the result to the output file
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # Close the clips
    final_clip.close()
    for clip in video_clips:
        clip.close()
    audio_clip.close()

    return output_path

def generate_video(story_prompt):
    story_json = generate_story(story_prompt)
    print(story_json)
    story_json_dict = json.loads(story_json)

    title = story_json_dict["title"]
    st.header(title)
    col1, col2, col3 = st.columns(3)
    video_logline = story_json_dict.get("video_logline", "")
    col1.subheader("Video Logline")
    col1.write(video_logline)
    voiceover_text = story_json_dict["voiceover_text"]
    col2.subheader("Voiceover Text")
    col2.write(voiceover_text)
    visual_style = story_json_dict.get("visual_style", "")
    col3.subheader("Visual Style")
    col3.write(visual_style)

    speech_path = generate_voiceover(voiceover_text)
    display_generated_media('voiceover', lambda *args, **kwargs: speech_path, col2, col3)
    
    video_paths = []    
    
    if "clips" in story_json_dict:
        for i, (clip_key, clip_value) in enumerate(story_json_dict["clips"].items()):
            image_prompt = clip_value.get("image_prompt", "")
            if image_prompt:
                # Generate and confirm each image and video
                st.subheader(f"Clip {i+1}")
                col1, col2, col3 = st.columns(3)
                full_prompt = f'{image_prompt} + {visual_style}'
                col1.subheader("Prompt:")
                col1.write(f"{full_prompt}")
                img_path = get_image_from_DALL_E_3_API(full_prompt)
       
                display_generated_media(f'image_{i}', lambda *args, **kwargs: img_path, col2, col3)
   
    
                video_path = get_video_from_Replicate_API(img_path)
                display_generated_media(f'video_{i}', lambda *args, **kwargs: video_path, col2, col3)
                video_paths.append(video_path)

    st.subheader("Final Video")

    if video_paths:
        output_video_path = f"media/videos/{title}.mp4"
        combine_videos_and_audio(video_paths, speech_path, output_video_path)
        print(f"Combined video and audio saved to {output_video_path}")
        st.write(f"Combined video and audio saved to {output_video_path}")
        # generate report with all prompts images and video
        report = {}
        report['title'] = title
        report['video_logline'] = video_logline
        report['voiceover_text'] = voiceover_text
        report['visual_style'] = visual_style
        report['clips'] = []
        for i, (clip_key, clip_value) in enumerate(story_json_dict["clips"].items()):
            clip = {}
            clip['image_prompt'] = clip_value.get("image_prompt", "")
            report['clips'].append(clip)
        with open(f"media/reports/{title}.json", 'w') as outfile:
            json.dump(report, outfile)

        return output_video_path

    else:
        print("No videos were generated.")
        st.write("No videos were generated.")



def display_generated_media(key, generate_media_function, col_image, col_video, *args, **kwargs):
    # Generate media if not already done or if regeneration is requested
    if key not in st.session_state or st.session_state.get(f'regenerate_{key}', False):
        st.session_state[key] = generate_media_function(*args, **kwargs)
        st.session_state[f'regenerate_{key}'] = False

    media_path = st.session_state[key]

    # Display the generated media based on its file type
    if media_path:
        file_extension = os.path.splitext(media_path)[1].lower()
        if file_extension in ['.jpg', '.jpeg', '.png']:
            col_image.subheader("Generated Image:")
            col_image.image(media_path)
        elif file_extension == '.mp3':
            st.subheader("Generated Audio:")
            st.audio(media_path)
        elif file_extension == '.mp4':
            col_video.subheader("Generated Video:")
            col_video.video(media_path)

def list_video_files(directory):
    """List video files in the given directory."""
    video_extensions = ['.mp4', '.avi', '.mov']  # Add more extensions as needed
    return [file for file in os.listdir(directory) if os.path.splitext(file)[1] in video_extensions]

def display_videos(video_files):
    """Display videos in rows of 3."""
    with st.expander("Example Gallery"):
        for i in range(0, len(video_files), 3):
            cols = st.columns(3)
            for j in range(3):
                index = i + j
                if index < len(video_files):
                    cols[j].video(os.path.join('media/videos', video_files[index]))




def main():
    st.set_page_config(page_title="X-Fiction", page_icon="🎥")
    st.title("X-Fiction Video Generation 🎥")
    
    st.image("media/header3.png")
    
    st.write("This is a demo. Enter a story prompt and click the 'Start Generation' button to generate a video. Generations take about 12 minutes. Progress can be followed live. Powered by Stable Video Diffusion.")
    
    # Initialize or use existing session state
    if 'current_story_prompt' not in st.session_state:
        st.session_state['current_story_prompt'] = "Reactions from hell (Genre: Satire)"    

    
    # Default story prompt
    story_prompt = st.text_input("Enter a story prompt", st.session_state['current_story_prompt'])

    col1, col2, col3 = st.columns(3)

    if col3.button("Generate Example Prompt"):
        example_prompts_json = generate_example_prompt()
        if example_prompts_json:
            example_prompts = json.loads(example_prompts_json)
            col1, col2, col3 = st.columns(3)
            for i, (prompt_key, prompt_value) in enumerate(example_prompts.items()):
                
                if i == 0:
                    col1.subheader("Prompt 1")
                    col1.write(prompt_value)
                elif i == 1:
                    col2.subheader("Prompt 2")
                    col2.write(prompt_value)
                elif i == 2:
                    col3.subheader("Prompt 3")
                    col3.write(prompt_value)
    if col1.button("Start Generation (0,80€)"):
        with st.spinner("Generating video..."):
            video_path = generate_video(story_prompt)
            col1, col2 = st.columns(2)
            col1.success("Video generated!")


            col2.video(video_path)   
    # Directory containing the videos
    video_directory = 'media/videos'

    # Get a list of video files
    videos = list_video_files(video_directory)

    # Display videos
    display_videos(videos)
        
   

if __name__ == "__main__":
    main()