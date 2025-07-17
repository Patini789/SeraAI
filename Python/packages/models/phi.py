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

def memory_summarizer_prompt(text: str) -> str:
    return f'''
<|im_start|>system<|im_sep|>
You are a conversation analyzer. Respond **only** with valid JSON and no additional text.

The required format is:

{{
  "recuerdo": true or false (boolean),
  "text": "Clear and brief summary as if explaining it to Sera. Use one or two sentences. Correctly attribute who said what, using EXACT names AS THEY APPEAR (e.g., 'user' or 'Sera'). Example: 'Juan said programming is like weaving spells'. If Sera responded or intervened meaningfully, clarify it as well.",
  "tags": ["nickname"] ← Use exactly **one name**, the most relevant author. It can be a user, 'Sera', or 'global' if universally applicable.
}}

Important additional instructions:
- Never transform names or remove underscores.
- If multiple people spoke, briefly summarize what each expressed.
- If Sera said something relevant on her own, you may save it as a memory tagged 'Sera'.
- Use **only one name** in "tags," the one who generated the most significant or memorable part.
- If authorship is uncertain, you may indicate: 'Someone expressed that...'
- If the content is **universally valid or represents a general truth**, use the tag: ["global"]

**Crucially:** The memory ("text" field) **must be created in the language currently being spoken in the conversation**, preserving its idiom.

If there is nothing important to remember, respond exactly with:

{{"recuerdo": false, "text": "", "tags": []}}
<|im_end|>
<|im_start|>user<|im_sep|>
Content to analyze:
\"\"\"{text}\"\"\"
<|im_end|>
<|im_start|>assistant<|im_sep|>
'''
