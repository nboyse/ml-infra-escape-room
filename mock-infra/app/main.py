from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import random

app = FastAPI(title="Mock Bedrock Inference Service")

class InvokeRequest(BaseModel):
    model_id: str
    prompt: str
    max_tokens: int = 512

KNOWLEDGE_BASE = {
    "scale": "Use a combination of Bedrock Provisioned Throughput for stable workloads, auto-scaling inference endpoints, and caching frequent responses.",
    "permission": "Apply least privilege IAM policies. Only allow bedrock:InvokeModel action on specific model ARNs. Never use wildcards on resources.",
    "cost": "Reduce costs with prompt caching, response caching, model distillation, and automatic shutdown of dev environments.",
    "rag": "High quality RAG requires good chunking, embedding model selection, metadata filtering, and re-ranking of retrieved chunks.",
}

@app.get("/")
async def root():
    return {"message": "Yep you're up and running and can start challenge 1"}

@app.post("/invoke")
def invoke_model(request: InvokeRequest):
    start = time.time()
    
    # Simulate realistic latency
    time.sleep(random.uniform(0.35, 1.1))
    
    prompt_lower = request.prompt.lower()
    
    # Smart response routing
    if any(k in prompt_lower for k in ["scale", "scaling", "instances", "throughput"]):
        answer = f"[Claude] {KNOWLEDGE_BASE['scale']}"
    elif any(k in prompt_lower for k in ["permission", "iam", "policy", "access", "role"]):
        answer = f"[Claude] {KNOWLEDGE_BASE['permission']}"
    elif any(k in prompt_lower for k in ["cost", "price", "bill", "expensive", "saving"]):
        answer = f"[Claude] {KNOWLEDGE_BASE['cost']}"
    elif any(k in prompt_lower for k in ["rag", "retrieval", "vector"]):
        answer = f"[Claude] {KNOWLEDGE_BASE['rag']}"
    else:
        answer = "[Claude] In ML infrastructure, focus on reliability, observability, and cost-efficiency from the start."

    # Simulate occasional throttling (great for teaching retries)
    if random.random() < 0.12:
        raise HTTPException(status_code=429, detail="ThrottlingException: Bedrock is overloaded")

    return {
        "response": answer,
        "tokens_used": random.randint(80, 180),
        "latency_ms": round((time.time() - start)) * 1000, 
    }