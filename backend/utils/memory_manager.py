# memory_manager.py
import json
import os

MEMORY_FILE = "conversation_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def remember_message(user_id, role, message):
    memory = load_memory()
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append({"role": role, "message": message})
    save_memory(memory)

def get_conversation_context(user_id):
    memory = load_memory()
    return memory.get(user_id, [])

def clear_user_memory(user_id):
    memory = load_memory()
    if user_id in memory:
        del memory[user_id]
    save_memory(memory)