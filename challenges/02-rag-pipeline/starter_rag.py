import requests
import time

BEDROCK_URL = "http://localhost:8000/invoke"

def simple_rag_query(question: str):
    # Terrible naive implementation - common anti-patterns
    prompt = f"Answer this: {question}"   # Almost no context or instructions
    
    try:
        response = requests.post(BEDROCK_URL, json={
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "prompt": prompt,
            "max_tokens": 150
        }, timeout=8)
        
        response.raise_for_status()
        return response.json()["response"]
        
    except Exception as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    print("Naive RAG Pipeline (Starter - Bad)\n")
    
    questions = [
        "How do we scale ML inference?",
        "What is the best way to handle permissions for Bedrock?",
        "How can we reduce inference costs?"
    ]
    
    for q in questions:
        print(f"Q: {q}")
        start = time.time()
        answer = simple_rag_query(q)
        latency = round((time.time() - start) * 1000)
        print(f"A: {answer}")
        print(f"Latency: {latency}ms\n")
        time.sleep(0.5)