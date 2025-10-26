from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
AI = OpenAI(api_key=os.getenv('API'), base_url="https://api.deepseek.com")