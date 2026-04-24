import os
import json
import re
import httpx
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

def get_client():
    """Returns an OpenAI client configured for LiteLLM or direct Anthropic."""
    base_url = os.environ.get("LITELLM_BASE_URL")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY", "sk-dummy")

    # Global timeout for the underlying httpx client (15 minutes)
    http_client = httpx.Client(timeout=900.0)
    
    if base_url:
        # LiteLLM/Ollama path
        return OpenAI(
            base_url=base_url,
            api_key=openai_api_key,
            http_client=http_client
        )
    else:
        # Fallback to direct Anthropic (requires LiteLLM locally or specific proxy)
        return OpenAI(
            base_url="https://api.anthropic.com/v1",
            api_key=anthropic_api_key or "sk-dummy",
            http_client=http_client
        )

def call_llm(prompt, system_prompt="You are a helpful assistant.", model=None, max_tokens=4000, temperature=0.7, json_mode=False, stream=True):
    """Unified LLM call supporting Anthropic and OpenAI-compatible endpoints with streaming for progress."""
    client = get_client()
    
    if not model:
        model = os.environ.get("AUTONOVEL_WRITER_MODEL", "claude-sonnet-4-6")

    print(f"Calling LLM ({model})...", flush=True)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    # Extra body params for LiteLLM/Ollama
    extra_body = {
        "include_reasoning": False,
        "options": {
            "num_predict": max_tokens if max_tokens > 0 else 4000,
            "temperature": temperature,
            "num_ctx": 262144 # Match the context window seen in ollama ps
        }
    }
    
    response_format = {"type": "json_object"} if json_mode else None

    try:
        if stream:
            full_content = ""
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,
                extra_body=extra_body,
                stream=True
            )
            print("Response: ", end="", flush=True)
            for chunk in response:
                delta = chunk.choices[0].delta
                content = delta.content or ""
                reasoning = getattr(delta, 'reasoning_content', None) or ""
                
                if reasoning:
                    # Print reasoning to show progress
                    print(reasoning, end="", flush=True)
                    # For current Ollama setup, the actual response might be in reasoning_content
                    full_content += reasoning
                
                if content:
                    print(content, end="", flush=True)
                    full_content += content
            print("\n") # New line after stream ends
            return full_content
        else:
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
