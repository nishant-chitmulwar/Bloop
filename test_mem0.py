from dotenv import load_dotenv
from mem0 import MemoryClient
import logging
import json
import os

load_dotenv(".env.local")
user_name = "Nishant"

# Initialize client properly
mem0 = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

def add_memory():
    messages_formatted = [
        {"role": "user", "content": "I really like Krishnakumar Kunnath."},
        {"role": "assistant", "content": "That is a good choice."},
        {"role": "user", "content": "I think so too."},
        {"role": "assistant", "content": "What is your favorite song by them?"},
    ]

    saved = mem0.add(messages_formatted, user_id=user_name)
    print("Saved memory:", saved)

def get_memory_by_query():
    query = f"What are {user_name}'s preferences?"
    results = mem0.search(query, user_id=user_name)

    memories = [
        {
            "memory": r.get("memory") or r.get("text") or r.get("message", ""),
            "updated_at": r.get("updated_at", "")
        }
        for r in (results.get("results") if isinstance(results, dict) else results)
    ]
    memories_str = json.dumps(memories, indent=2)
    print(f"Memories: {memories_str}")
    return memories_str

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_memory()
    get_memory_by_query()
