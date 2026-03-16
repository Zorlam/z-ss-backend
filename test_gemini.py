import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("AIzaSyCrg9KlXQI4NulkpgvsymOEfT07LzVSTkg"))

print("Available Gemini models:")
for model in client.models.list():
    print(f"- {model.name}")