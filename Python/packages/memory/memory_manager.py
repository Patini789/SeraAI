"""MemoryManager class
bulk_add
filter_by_tag
delete_memory(id)

"""
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone

class MemoryManager:
    def __init__(self, json_path, api_client, embedding_dim = 348):
        self.api_client = api_client
        self.json_path = json_path
        self.embedding_dim = embedding_dim
        self.memories = [] #List of: id, text, tags, timestamp, embedding
        self._load_memories()


    def _load_memories(self):
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding="utf-8") as f:
                    self.memories = json.load(f)
                for mem in self.memories:
                    mem["embedding"] = np.array(mem["embedding"], dtype=np.float32)
            except Exception as e:
                print(e)
                self.memories = []
        else:
            with open(self.json_path, 'w', encoding="utf-8") as f:
                json.dump([], f)

    def _save_memories(self):
        serializable = []
        for mem in self.memories:
            serializable.append({
                "id": mem["id"],
                "text": mem["text"],
                "tags": mem["tags"],
                "timestamp": mem["timestamp"],
                # Save as list
                "embedding": mem["embedding"].tolist()
            })
        with open(self.json_path, 'w', encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=4)

    def add_memory(self, text, tags=None, timestamp=None, embedding=None):
        """
        Add a new memory.
        - text: the content to store.
        - tags: list of strings for simple tag-based filtering.
        - timestamp: ISO format string; if None, current UTC time is used.
        - embedding: numpy array of shape (embedding_dim,) if precomputed. If None, a placeholder random vector is used.
        """
        if tags is None:
            tags = []
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        if embedding is None:
            embedding = np.random.random(self.embedding_dim).astype(np.float32)
        mem_id = f"mem_{len(self.memories)+1:04d}"

        self.memories.append({
            "id": mem_id,
            "text": text,
            "tags": tags,
            "timestamp": timestamp,
            "embedding": embedding
        })
        self._save_memories()
        return mem_id

    def search_memories(self, query_embeddings, top_k=5, tag_filter=None):
        """
        Search memories by cosine similarity to the query_embedding.
        - query_embedding: numpy array of shape (embedding_dim,).
        - top_k: number of top results to return.
        - tag_filter: list of tags; if provided, only memories containing any of these tags are considered.
        Returns list of (memory_dict, similarity_score).
        """
        if len(self.memories) == 0:
            return []
        candidates = self.memories

        if tag_filter is not None:
            candidates = [mem for mem in self.memories if any(tag in mem["tags"] for tag in tag_filter)]
            if not candidates:
                return []

        # Build a matrix... matrix? lets escape.
        emb_matrix = np.stack([mem["embedding"] for mem in candidates], axis=0)
        #Normalice for cousin similitude
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)

        emb_matrix = emb_matrix / np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        q_norm = query_embeddings / np.linalg.norm(query_embeddings)

        sims = emb_matrix.dot(q_norm)

        # Get top_k most relevant index
        top_index = np.argsort(-sims)[:top_k]
        results = [(candidates[i], float(sims[i])) for i in top_index]
        return results

    def to_dataframe(self):
        """
        Return a pandas dataframe containing all memories. without the embedding column
        """
        data = []
        for mem in self.memories:
            data.append({
                "id": mem["id"],
                "text": mem["text"],
                "tags": mem["tags"],
                "timestamp": mem["timestamp"],
                "embedding_dim": len(mem["embedding"]),
            })
        return pd.DataFrame(data)

    def retrieve(self, text: str, top_k: int = 5, min_similarity: float = 0.8, tags: list[str] = None) -> list[str]:
        try:
            query_emb = self.api_client.embed(text)
            results = self.search_memories(query_emb, top_k=top_k, tag_filter=tags)
            filtered = [mem["text"] for mem, score in results if score >= min_similarity]
            return filtered
        except Exception as e:
            print(f"❌ Memory retrieval error: {e}")
            return []

    def name(self):
        return "MemoryManager"


