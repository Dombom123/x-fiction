import requests
from pathlib import Path

class ImageDownloader:
    def __init__(self, download_path='downloaded_images'):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)

    def download_image(self, url, file_name):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                image_path = self.download_path / f"{file_name}.png"
                with open(image_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                return image_path
            else:
                raise Exception(f"Failed to download image: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

# Example usage
if __name__ == "__main__":
    downloader = ImageDownloader()
    image_url = "https://i.ibb.co/bszCKKS/7.png"  # Replace with a real image URL
    file_name = "test_image"
    downloaded_image_path = downloader.download_image(image_url, file_name)
    print(f"Downloaded image path: {downloaded_image_path}")
