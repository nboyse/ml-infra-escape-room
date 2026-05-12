import requests
import time

BEDROCK_URL = "http://localhost:8000/invoke"

def call_bedrock(prompt: str, max_tokens: int = 300):
    """Make a call and return both response and real token usage"""
    response = requests.post(BEDROCK_URL, json={
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "prompt": prompt,
        "max_tokens": max_tokens
    }, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    return {
        "response": data["response"],
        "tokens_used": data.get("tokens_used", 0)
    }


def research_agent(question: str):
    print(f"Researching: {question}\n")
    total_tokens = 0
    start_time = time.time()
    
    # Expensive and Wasteful Pattern
    
    # 1 - Broad research
    p1 = f"Research everything you can about: {question}"
    res1 = call_bedrock(p1, 450)
    total_tokens += res1["tokens_used"]
    print(f"Step 1 completed ({res1['tokens_used']} tokens)\n")
    
    # 2 - Critique (usually unnecessary)
    p2 = f"Critique and improve this answer: {res1['response']}"
    res2 = call_bedrock(p2, 400)
    total_tokens += res2["tokens_used"]
    print(f"Step 2 completed ({res2['tokens_used']} tokens)\n")
    
    # 3 - Make it longer (very wasteful)
    p3 = f"Expand this answer with more details and examples: {res2['response']}"
    res3 = call_bedrock(p3, 500)
    total_tokens += res3["tokens_used"]
    print(f"Step 3 completed ({res3['tokens_used']} tokens)\n")
    
    # 4 - Final summary
    p4 = f"Provide a clean, professional final answer based on this: {res3['response']}"
    final = call_bedrock(p4, 350)
    total_tokens += final["tokens_used"]
    
    elapsed = round(time.time() - start_time, 2)
    
    print(f"\n{'='*70}")
    print("FINAL ANSWER:")
    print(final["response"])
    print(f"\nTotal tokens used: {total_tokens:,}")
    print(f"Total time: {elapsed} seconds")
    print("This agent is expensive!")
    
    return final["response"]


if __name__ == "__main__":
    question = "Best practices for scaling ML inference with Amazon Bedrock"
    research_agent(question)