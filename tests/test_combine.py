from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

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

def main():
    # test combine_videos_and_audio
    video_paths = ["clips/video_img_A futuristic spacecraft leaving the Earth's atmosp.mp4", "clips/video_img_A group of astronauts in a spacecraft observation .mp4", "clips/video_img_The Perseverance maneuvering deftly between massiv.mp4", "clips/video_img_The remnants of a lost alien city with glowing ins.mp4", "clips/video_img_The contented faces of the crew members sharing st.mp4"]
    audio_path = "speech.mp3"
    output_path = "output.mp4"
    combine_videos_and_audio(video_paths, audio_path, output_path)
    print("done")

if __name__ == "__main__":
    main()