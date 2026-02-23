from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    models = client.models.list()
    print("Available models:")
    for model in models:
        print(f"- {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")