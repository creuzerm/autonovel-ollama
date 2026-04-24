import os
from llm import call_llm

def test_model(name, model, include_reasoning=True):
    print(f"\n=== Testing {name}: {model} ===")
    
    print(f"--- 1. {name} Standard Call (No Streaming) ---")
    try:
        response = call_llm(
            prompt="Say 'Connectivity Test: Success' and nothing else.",
            system_prompt="You are a helpful assistant.",
            model=model,
            max_tokens=20,
            stream=False,
            include_reasoning=include_reasoning
        )
        print(f"Final Response: {response.strip()}")
    except Exception as e:
        print(f"Standard Call Failed: {e}")

    print(f"\n--- 2. {name} Streaming Call ---")
    try:
        response = call_llm(
            prompt="Count from 1 to 3 slowly.",
            system_prompt="You are a helpful assistant.",
            model=model,
            max_tokens=50,
            stream=True,
            include_reasoning=include_reasoning
        )
        print(f"Final Streamed Content: {response.strip()}")
    except Exception as e:
        print(f"Streaming Call Failed: {e}")

def run_comprehensive_test():
    writer_model = os.environ.get("AUTONOVEL_WRITER_MODEL")
    judge_model = os.environ.get("AUTONOVEL_JUDGE_MODEL")
    
    print(f"LITELLM_BASE_URL: {os.environ.get('LITELLM_BASE_URL')}")
    
    if writer_model:
        # Test writer with reasoning
        test_model("Writer", writer_model, include_reasoning=True)
        # Test writer without reasoning
        test_model("Writer (No Reasoning)", writer_model, include_reasoning=False)
        
    if judge_model:
        test_model("Judge", judge_model, include_reasoning=False)

if __name__ == "__main__":
    run_comprehensive_test()
