# Import os so environment variables can be accessed
import os

# Load variables stored in the .env file
from dotenv import load_dotenv

# Import the Google GenAI library for direct Gemini API communication
from google import genai

# Import the LangChain wrapper for Google Gemini models
from langchain_google_genai import ChatGoogleGenerativeAI


# Load environment variables from the .env file
load_dotenv()


# Read the Gemini API key from the environment
# Keeping the API key in .env prevents it from being hard-coded in the source code
api_key = os.getenv("GEMINI_API_KEY")


# Check that the API key exists before creating the Gemini clients
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from the environment."
    )


# Create the standard Google GenAI client
# This client is used when Gemini is called directly without LangChain
client = genai.Client(api_key=api_key)


def generate_response(prompt: str) -> str:
    """
    Send a text prompt directly to Gemini and return the generated response.

    Args:
        prompt: The text instruction that will be sent to Gemini.

    Returns:
        The generated response as a cleaned string.
    """

    try:
        # Send the supplied prompt to the Gemini model
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        # Remove unnecessary whitespace before returning the response
        return response.text.strip()

    except Exception as error:
        # Convert Gemini/API errors into a clear application-level error
        # This allows the agent layer to handle the failure later
        raise RuntimeError(
            f"Gemini request failed: {error}"
        ) from error


def get_langchain_model():
    """
    Create and return a Gemini chat model configured for LangChain.

    This model will be used by the task assistant agent when working
    with LangChain prompt templates, chains, and tools.
    """

    # Create the Gemini model through LangChain
    # temperature=0 is used to make responses more consistent
    # for structured task-management suggestions
    return ChatGoogleGenerativeAI(
        model="gemini-3.7-flash",
        temperature=0,
        google_api_key=api_key
    )