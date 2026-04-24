import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# API Configuration
LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-dummy")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def get_client():
    """Returns an OpenAI client configured for LiteLLM or direct Anthropic (via LiteLLM)."""
    if LITELLM_BASE_URL:
        return OpenAI(
            base_url=LITELLM_BASE_URL,
            api_key=OPENAI_API_KEY
        )
    else:
        # Fallback to direct Anthropic if no LiteLLM base URL is provided
        # Note: This still uses the OpenAI client format, which LiteLLM supports.
        # If the user wants direct Anthropic without LiteLLM, they should use LiteLLM locally.
        # However, to maintain the requested 'standard OpenAI Python client' approach:
        return OpenAI(
            base_url="https://api.anthropic.com/v1", # This might not work directly with OpenAI client for Anthropic
            api_key=ANTHROPIC_API_KEY
        )

def call_llm(prompt, system_prompt="You are a helpful assistant.", model=None, max_tokens=4000, temperature=0.7, json_mode=False):
    """
    Unified LLM call that supports both Anthropic and OpenAI-compatible endpoints via LiteLLM.
    """
    client = get_client()
    
    if not model:
        model = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    extra_body = {}
    # LiteLLM/Ollama specific context window handling can be passed here if needed
    
    response_format = {"type": "json_object"} if json_mode else None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format,
            extra_body=extra_body
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise

def parse_json_response(text):
    """Cleanly parse JSON from LLM response."""
    import re
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    
    # Find the outermost JSON object
    start = text.find('{')
    if start == -1:
        # Try to find an array if no object
        start = text.find('[')
        if start == -1:
            raise ValueError("No JSON object or array found in response")
            
    # Simple search for the last brace/bracket
    end = text.rfind('}')
    if end == -1:
        end = text.rfind(']')
    
    if end == -1 or end < start:
        raise ValueError("Invalid JSON structure in response")
        
    return json.loads(text[start:end+1], strict=False)
