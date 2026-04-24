import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

def get_client():
    """Returns an OpenAI client configured for LiteLLM or direct Anthropic."""
    base_url = os.environ.get("LITELLM_BASE_URL")
    
    if base_url:
        # LiteLLM/Ollama path
        return OpenAI(
            base_url=base_url,
            api_key=os.environ.get("OPENAI_API_KEY", "sk-dummy")
        )
    else:
        # Fallback to direct Anthropic (requires LiteLLM locally or specific proxy)
        # Note: If no LITELLM_BASE_URL, we default to Anthropic's URL.
        # Anthropic doesn't support the OpenAI SDK natively without a proxy,
        # so this assumes the user is using one or provided a LITELLM_BASE_URL.
        return OpenAI(
            base_url="https://api.anthropic.com/v1",
            api_key=os.environ.get("ANTHROPIC_API_KEY", "sk-dummy")
        )

def call_llm(prompt, system_prompt="You are a helpful assistant.", model=None, max_tokens=4000, temperature=0.7, json_mode=False):
    """Unified LLM call supporting Anthropic and OpenAI-compatible endpoints."""
    client = get_client()
    
    if not model:
        model = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    response_format = {"type": "json_object"} if json_mode else None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format,
            extra_body={}
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise

def parse_json_response(text):
    """Cleanly parse JSON (object or array) from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    
    # Find the FIRST occurrence of either { or [
    obj_start = text.find('{')
    arr_start = text.find('[')
    
    if obj_start == -1 and arr_start == -1:
        raise ValueError("No JSON object or array found in response")
        
    if obj_start != -1 and (arr_start == -1 or obj_start < arr_start):
        # Starts with an object
        start = obj_start
        end = text.rfind('}')
    else:
        # Starts with an array
        start = arr_start
        end = text.rfind(']')
    
    if end == -1 or end < start:
        raise ValueError("Invalid JSON structure in response")
        
    return json.loads(text[start:end+1], strict=False)
