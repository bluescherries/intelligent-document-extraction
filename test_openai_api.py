import os

from dotenv import load_dotenv
from openai import OpenAI


# Load variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found in .env"
    )

# Create OpenAI client
client = OpenAI(
    api_key=api_key
)


# Make a simple API request
response = client.responses.create(
    model="gpt-5.6-luna",
    input="Say hello and confirm that you are working."
)


print("OpenAI API call successful!")
print()
print("Model response:")
print(response.output_text)