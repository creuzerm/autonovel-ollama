import pytest
import os
import json
import openai
from llm import get_client, call_llm, parse_json_response

# ============================================================
# CONFIGURATION & ROUTING TESTS
# ============================================================

def test_get_client_litellm(monkeypatch):
    """Verify client routes to LiteLLM when configured."""
    monkeypatch.setenv("LITELLM_BASE_URL", "http://192.168.86.42:4000")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    
    client = get_client()
    
    # OpenAI client appends / to the base_url internally
    assert str(client.base_url).rstrip("/") == "http://192.168.86.42:4000"
    assert client.api_key == "sk-test-key"

def test_get_client_anthropic_fallback(monkeypatch):
    """Verify client falls back to Anthropic URL when LiteLLM is missing."""
    monkeypatch.delenv("LITELLM_BASE_URL", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    
    client = get_client()
    
    assert "api.anthropic.com" in str(client.base_url)
    assert client.api_key == "sk-ant-test"


# ============================================================
# PAYLOAD & ORCHESTRATION TESTS
# ============================================================

def test_call_llm_payload_formatting(mocker, monkeypatch):
    """Verify call_llm passes correct parameters to the OpenAI client."""
    monkeypatch.setenv("AUTONOVEL_WRITER_MODEL", "ollama/qwen3.6")
    # Need keys to prevent get_client from failing even if we mock create
    monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy")
    monkeypatch.setenv("LITELLM_BASE_URL", "http://localhost:4000")
    
    # Mock the OpenAI client's chat.completions.create method
    # We patch the instance level create method
    mock_create = mocker.patch("openai.resources.chat.completions.Completions.create")
    mock_create.return_value = mocker.Mock(
        choices=[mocker.Mock(message=mocker.Mock(content="Generated text"))]
    )
    
    call_llm(
        prompt="Write a scene.",
        system_prompt="You are a poet.",
        max_tokens=500,
        temperature=0.5,
        json_mode=True
    )
    
    # Assert formatting matches OpenAI/LiteLLM spec
    mock_create.assert_called_once_with(
        model="ollama/qwen3.6",
        messages=[
            {"role": "system", "content": "You are a poet."},
            {"role": "user", "content": "Write a scene."}
        ],
        max_tokens=500,
        temperature=0.5,
        response_format={"type": "json_object"},
        extra_body={}
    )


# ============================================================
# JSON PARSING ROBUSTNESS TESTS (Dirty LLM Output)
# ============================================================

def test_parse_clean_json():
    """Test standard JSON parsing."""
    data = '{"score": 8.5, "verdict": "Good"}'
    assert parse_json_response(data) == {"score": 8.5, "verdict": "Good"}

def test_parse_markdown_fenced_json():
    """Test JSON wrapped in markdown fences (common LLM behavior)."""
    data = "```json\n{\n  \"score\": 10,\n  \"note\": \"Perfect\"\n}\n```"
    assert parse_json_response(data) == {"score": 10, "note": "Perfect"}

def test_parse_json_with_noisy_preamble():
    """Test JSON with conversational filler (common LLM behavior)."""
    data = "I have evaluated the chapter. Here is the result:\n\n{\"eval\": \"pass\"}\n\nI hope this helps!"
    assert parse_json_response(data) == {"eval": "pass"}

def test_parse_json_array():
    """Test parsing of JSON arrays."""
    data = "The list is:\n[{\"id\": 1}, {\"id\": 2}]"
    assert parse_json_response(data) == [{"id": 1}, {"id": 2}]

def test_parse_invalid_json_raises_error():
    """Verify that genuinely invalid JSON still raises an error."""
    data = "This is not JSON at all."
    with pytest.raises(ValueError, match="No JSON object or array found"):
        parse_json_response(data)


# ============================================================
# NETWORK RESILIENCE TESTS (Mocked Errors)
# ============================================================

def test_call_llm_handles_api_error(mocker, monkeypatch):
    """Verify call_llm raises on API errors (e.g., Ollama down)."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy")
    monkeypatch.setenv("LITELLM_BASE_URL", "http://localhost:4000")
    
    mock_create = mocker.patch("openai.resources.chat.completions.Completions.create")
    mock_create.side_effect = openai.APIStatusError(
        message="Ollama Server Error",
        response=mocker.Mock(status_code=500),
        body=None
    )
    
    with pytest.raises(openai.APIStatusError):
        call_llm("Test prompt")
