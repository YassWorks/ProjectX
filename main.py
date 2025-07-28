from dotenv import load_dotenv
import os
from app import Agent
# import textwrap

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = "qwen-3-32b"

# system_prompt = textwrap.dedent(input().strip())

directory = os.path.dirname(os.path.abspath(__file__))
system_prompt_path = os.path.join(directory, "system_prompt.txt")
with open(system_prompt_path, "r") as file:
    system_prompt = file.read().strip()
    
# print(system_prompt)

agent = Agent(
    model_name=MODEL_NAME,
    api_key=API_KEY,
    system_prompt=system_prompt
)

agent.start_chat()