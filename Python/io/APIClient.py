"""
#api_client.py
Send a prompt to the model host and return the response.
"""

import requests
import numpy as np


class APIClient:
    def __init__(self, embedding_url: str, embedding_model: str,
                       completion_url: str, completion_model: str) -> None:
        self.embed_url = embedding_url
        self.embed_model = embedding_model
        self.complete_url = completion_url
        self.complete_model = completion_model

    def embed(self, text: str):
        payload = {"input": text, "model": self.embed_model}
        resp = requests.post(self.embed_url, json=payload, timeout=30)
        resp.raise_for_status()
        emb = resp.json()["data"][0]["embedding"]
        return np.array(emb, dtype=np.float32)

    def complete(self, prompt: str, **kwargs) -> str:
        payload = {"model": self.complete_model, "prompt": prompt, **kwargs}
        resp = requests.post(self.complete_url, json=payload, timeout=400)
        resp.raise_for_status()
        choices = resp.json().get("choices", [])
        return choices[0]["text"].strip() if choices else ""
