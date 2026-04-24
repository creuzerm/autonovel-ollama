from llm import call_llm

def run_quick_test():
    print("--- 1. Testing Standard Call (No Streaming) ---")
    try:
        response = call_llm(
            prompt="Say 'Connectivity Test: Success' and nothing else.",
            system_prompt="You are a helpful assistant.",
            max_tokens=20,
            stream=False
        )
        print(f"Final Response: {response.strip()}")
    except Exception as e:
        print(f"Standard Call Failed: {e}")

    print("\n--- 2. Testing Streaming Call ---")
    try:
        # call_llm defaults to stream=True in its current implementation
        response = call_llm(
            prompt="Count from 1 to 5 slowly.",
            system_prompt="You are a helpful assistant.",
            max_tokens=50,
            stream=True
        )
        print(f"\nFinal Streamed Content: {response.strip()}")
    except Exception as e:
        print(f"Streaming Call Failed: {e}")

if __name__ == "__main__":
    run_quick_test()
