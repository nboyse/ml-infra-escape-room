from locust import HttpUser, task, between
import random

class MLInferenceUser(HttpUser):
    wait_time = between(0.5, 1.8)
    
    @task(5)
    def normal_inference(self):
        self.client.post("/invoke", json={
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "prompt": "Explain machine learning infrastructure scaling best practices.",
            "max_tokens": 400
        }, timeout=10)

    @task(1)
    def heavy_inference(self):
        """Simulates poorly written RAG and long context"""
        self.client.post("/invoke", json={
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "prompt": "x" * 12000,
            "max_tokens": 2000
        }, timeout=15)

    @task(2)
    def realistic_rag_query(self):
        """A more realistic RAG query"""
        prompts = [
            "How do we scale ML inference efficiently?",
            "Best practices for Bedrock IAM permissions?",
            "How can we reduce Bedrock inference costs?"
        ]
        self.client.post("/invoke", json={
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "prompt": random.choice(prompts),
            "max_tokens": 350
        })