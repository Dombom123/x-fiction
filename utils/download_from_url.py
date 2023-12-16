import requests
from pathlib import Path

def download_video_from_url(url, output_path):
    """
    Download a video from a URL and save it to a file.

    :param url: URL of the video to download.
    :param output_path: Path where the video file will be saved.
    :return: Path to the saved video file.
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # Downloading in chunks of 1 MB
                video_file.write(chunk)
        return output_path
    else:
        print(f"Failed to download video. Status code: {response.status_code}")
        return None

# Example usage
video_url = "https://replicate.delivery/pbxt/TbxBrGUhebScPSMs53TgNew2xcwQnHo4fDeb3LIIdRA7jWLIB/000021.mp4"  # Replace with the actual video URL
output_video_path = "media/clips/my_video.mp4"  # Replace with your desired output path
download_video_from_url(video_url, output_video_path)
