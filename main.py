from dotenv import load_dotenv
import os
from app import Agent

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = "qwen-3-32b"

agent = Agent(
    model_name=MODEL_NAME,
    api_key=API_KEY
)

agent.start_chat()