from openai import OpenAI
import replicate

class APIManager:
    def __init__(self, openai_api_key, replicate_api_key):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.replicate_client = replicate.Client(token=replicate_api_key)

    def generate_example_prompt(self, system_prompt):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate three very short example prompts for the Dreammachine"}
                ],
                response_format={"type": "json_object"},
                temperature=1.0,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred in generate_example_prompt: {e}")
            return None

    def generate_story(self, story_prompt, system_prompt):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": story_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=1.0,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred in generate_story: {e}")
            return None

    # Additional methods for other API interactions...
