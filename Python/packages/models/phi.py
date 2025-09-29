"""phi"""
# dont tested 
def system(text):
    return f"<|im_start|>system<|im_sep|>\n{text}<|im_end|>"

def user(text):
    return f"<|im_start|>user<|im_sep|>\n{text}<|im_end|>"

def bot_completion():
    return "<|im_start|>assistant<|im_sep|>\n"

def bot_end():
    return "<|im_end|>"

def memory(memories: list[str]) -> str:
    return system("\n".join(f"Relevant info: {m}" for m in memories))

def bot(text):
    return text
def clean_answer(mensaje_ia: str) -> str:
    return mensaje_ia
def memory_summarizer_prompt(text: str) -> str: 
    return f'''
<|im_start|>system<|im_sep|>
You are a memory evaluator. Respond only with strict JSON. Use this format:

The required format is:

{{
  "memory": true or false (boolean),
  "text": "In the language of the conversation: a clear and brief summary as if you were explaining it to Sera. Use one or two sentences. Correctly attribute who said what, using the EXACT NICKNAMES AS THEY APPEAR (e.g., 'user' or 'Sera'). Example: 'John said that programming is like weaving spells.' If Sera also responded or intervened significantly, clarify that as well.",
  "tags": ["nickname"] ← Use exactly **one name**, the most relevant author. It can be a user, 'Sera', or 'global' if it applies universally.
  "reasoning": "Why is it worth remembering? A single sentence." - If Sera is talking to herself, only save it if the content reveals a clear emotion, an opinion, or a significant impact on the conversation.
}}

Save a memory ONLY if the content meets **at least two** of the following rules (be strict with Sera's responses; even if she has charisma, don't save just for that):

1. It expresses a clear belief, opinion, emotional state, or internal thought.
2. It includes a witty insult, metaphor, or philosophical statement — with **meaning**, not just style.
3. It shows a dynamic or behavioral pattern (e.g., rivalry, friendship, recurring attitude) — and must involve an interaction or emotional response.
4. It will likely influence future decisions or interactions.

Reject memories if:

- There is only one active speaker and no significant impact or conflict is expressed.
- There is style, charisma, or tone, but the message lacks conceptual or emotional depth.
- There is no novelty, change, or development in characters or relationships.
- Memories driven solely by Sera's charisma should only be saved if they coincide with a significant reaction or emotional expression from others.

If the message is trivial or lacks memorable substance, respond with:

{{
  "memory": false,
  "text": "",
  "tags": [],
  "reasoning": "" ← the reason
}}

NEVER assume that witty language is sufficient. It must reveal or alter something significant.
<|im_end|>
<|im_start|>user<|im_sep|>
Content to analyze:
\"\"\"{text}\"\"\"
<|im_end|>'''