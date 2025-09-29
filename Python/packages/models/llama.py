"""Llama"""

def system(text):
    return f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{text}<|eot_id|>"

def user(text):
    return f"<|start_header_id|>user<|end_header_id|>\n{text}<|eot_id|>"

def bot_completion():
    return "<|start_header_id|>assistant<|end_header_id|>\n"

def bot_end():
    return "<|eot_id|>\n"

def memory(memories: list[str]) -> str:
    return "\n".join(f"Relevant info: {m}" for m in memories)

def translator_to_english(message: str) -> str:
    return f"<|start|>developer<|message|>\nTranslate this text to english do not add nothing more just your answer, the person how is normally refered ys Sera, if you see take like a name<|end|><|start|>user<|message|>\n{message}<|end|>"

def translator_to_spanish(message: str) -> str:
    return f"<|start|>developer<|message|>\nTraduce este texto al español no añadas más que la respuesta<|end|><|start|>user<|message|>\n{message}<|end|>"

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
  "recuerdo": true or false (boolean),
  "text": "Clear and brief summary as if explaining it to Sera. Use one or two sentences. Correctly attribute who said what, using EXACT names AS THEY APPEAR (e.g., 'user' or 'Sera'). Example: 'Juan said programming is like weaving spells'. If Sera responded or intervened meaningfully, clarify it as well. In the language of the conversation",
  "tags": ["nickname"] ← Use exactly **one name**, the most relevant author. It can be a user, 'Sera', or 'global' if universally applicable.
  "reasoning": "Why is this worth remembering? One sentence."- If Sera speaks alone, save only if content reveals clear emotional depth, opinion, or impacts the conversation in a meaningful way.

}}

Memory must be saved ONLY if the content fulfills **at least two** of these, be strict with Sera answers, she ever have charisma, do not save just for her:

1. Expresses a clear belief, opinion, emotional state, or internal thought.
2. Includes a clever insult, metaphor, or philosophical statement — with **meaning**, not just style.
3. Shows a dynamic or behavioral pattern (e.g., rivalry, friendship, recurring attitude) — and must involve a back-and-forth or emotional response.
4. Will likely influence future decisions or interactions.

Reject memories if:

- Only one speaker is active and no meaningful impact or conflict is expressed.
- Style, charisma, or tone is present but the message lacks conceptual or emotional depth.
- There is no novelty, change, or development in character or relationships.
- Memories primarily driven by Sera’s charisma or style alone should be saved only if they coincide with a meaningful reaction or emotional expression by others.

If the message is trivial or lacks memorable substance, reply:

{{
  "recuerdo": false,
  "text": "",
  "tags": [],
  "reasoning": "Fails to meet any rule. No emotional content, opinion, dynamic, or novelty."
}}

NEVER assume clever wording is enough. It must reveal or alter something significant.

<|im_end|>
<|im_start|>user<|im_sep|>
Content to analyze:
\"\"\"{text}\"\"\"
<|im_end|>
<|im_start|>assistant<|im_sep|>
'''
