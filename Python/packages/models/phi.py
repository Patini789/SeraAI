"""phi"""

def system(text):
    print(text)
    return f"<|im_start|>system<|im_sep|>\n{text}<|im_end|>"

def user(text):
    print(text)
    return f"<|im_start|>user<|im_sep|>\n{text}<|im_end|>"

def bot_completion():
    return "<|im_start|>assistant<|im_sep|>\n"

def bot_end():
    return ""

def memory(memories: list[str]) -> str:
    return "\n".join(f"Relevant info: {m}" for m in memories)

def bot(text):
    print(f"Phi Message read: {text}")
    return text