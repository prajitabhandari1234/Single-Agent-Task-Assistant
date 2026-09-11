# Import os to read environment variables
import os

# Load variables stored in the .env file
from dotenv import load_dotenv

# Import the Google GenAI library for Gemini
from google import genai


# Load environment variables from the .env file
load_dotenv()


# Read the Gemini API key from the environment
api_key = os.getenv("GEMINI_API_KEY")


# Check that the API key exists before creating the client
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from the environment."
    )


# Create the Gemini client
client = genai.Client(api_key=api_key)


def generate_response(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated text.
    """

    try:
        # Send the prompt to the Gemini model
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        # Return the generated response as clean text
        return response.text.strip()

    except Exception as error:
        # Raise a clear error so the agent can handle it later
        raise RuntimeError(
            f"Gemini request failed: {error}"
        ) from error