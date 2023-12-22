
# Multimedia Content Generator

![alt text](https://github.com/dombom123/x-fiction/blob/main/media/header3.png?raw=true)

## Description

The Multimedia Content Generator is an innovative project leveraging the capabilities of OpenAI's GPT-4 and DALL-E-3 models, along with the Replicate API. It is designed to autonomously create a cohesive multimedia story. Given a user prompt, the system generates a narrative, accompanying voiceover, illustrative images, and synthesized videos, culminating in an integrated multimedia experience.

## Features

- **Story Generation**: Utilizes OpenAI's GPT-4 model to craft compelling stories from user-provided prompts.
- **Voiceover Creation**: Converts the generated story into a voiceover using OpenAI's Text-to-Speech API.
- **Image Generation**: Produces vivid images corresponding to specific story segments through OpenAI's DALL-E-3 model.
- **Video Synthesis**: Transforms the generated images into dynamic videos via the Replicate API.
- **Multimedia Integration**: Seamlessly merges the voiceover and videos into a unified video narrative.

## Installation

1. **Clone the Repository**: `git clone https://github.com/dombom123/x-fiction.git`
2. **Install Dependencies**: Run `pip install -r requirements.txt` to install the necessary Python packages.

### Setting Up

- **Configure API Keys**: Create a `.streamlit/secrets.toml` file like the provided example file `.streamlit/secrets.example.toml`

## Usage

Start the Streamlit Frontend:

streamlit run x-main.py

The script processes your prompt to generate a story, voiceover, images, and videos, ultimately combining them into a single multimedia file.

## Contributing

Your contributions can help grow and improve this project! To contribute:

1. **Fork the Repository**: Create your own fork of the project.
2. **Create a Feature Branch**: Work on your new feature in a separate branch.
3. **Commit Your Changes**: Add meaningful commit messages describing your changes.
4. **Push to the Branch**: Upload your changes to your fork.
5. **Open a Pull Request**: Submit a pull request for review.

Thank you for your interest in contributing to the Multimedia Content Generator!

## License

This project is released under the [MIT License].

## Contact

For inquiries or collaboration, reach out via:

- **Email**: dominik@drivebeta.de
