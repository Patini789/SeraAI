"""gpt"""

def system(text):
    return f"<|start|>system<|message|> \nReasoning: LOW\n <|end|><|start|>developer<|message|>\n{text}<|end|>"

def user(text):
    return f"<|start|>user<|message|>\n{text}<|end|>"

def bot_completion():
    return "<|start|>assistant\n"

def bot_end():
    return "<|end|>"

def developer(text):
    return f"<|start|>developer<|message|>\n{text}<|end|>"

def translator_to_english(message: str) -> str: # just translation for spanish to english
    # TODO add a custom language option
    return f"<|start|>system<|message|> \nReasoning: LOW\n <|end|><|start|>developer<|message|>\nTranslate this text to english do not add nothing more just your answer, the person how is normally refered is Sera, if you see take like a name<|end|><|start|>user<|message|>\n{message}<|end|>"

def translator_to_spanish(message: str) -> str:
    return f"<|start|>system<|message|> \nReasoning: LOW\n <|end|><|start|>developer<|message|>\nTraduce este texto al español no añadas más que la respuesta<|end|><|start|>user<|message|>\n{message}<|end|>"

def clean_answer(mensaje_ia: str) -> str:
    print(mensaje_ia)
    marcador1 = "<|message|>"
    marcador2 = "<|constrain|>"

    index = mensaje_ia.rfind(marcador1)
    if index != -1:
        return mensaje_ia[index + len(marcador1):].strip()

    index = mensaje_ia.rfind(marcador2)
    if index != -1:
        return mensaje_ia[index + len(marcador2):].strip()

    return mensaje_ia.strip()



def memory(memories: list[str]) -> str:
    return system("\n".join(f"Relevant info: {m}" for m in memories))

def bot(text):
    return text

def memory_summarizer_prompt(text: str) -> str:
    return f'''
<|start|>system<|message|>
You are a memory evaluator. Respond only with strict JSON. Use this format:

The required format is:

{{
  "memory": true or false (boolean),
  "text": "In the language of the conversation: a clear and brief summary as if you were explaining it to Sera. Use one or two sentences. Correctly attribute who said what, using the EXACT NICKNAMES AS THEY APPEAR (for example, 'user' or 'Sera'). Example: 'Juan said that programming is like weaving spells.' If Sera responded or intervened significantly, clarify that as well.",
  "tags": ["nickname"] ← Use exactly **one name**, the most relevant author. It can be a user, 'Sera', or 'global' if it applies universally.
  "reasoning": "Why is it worth remembering? A single sentence." - If Sera speaks alone, save only if the content reveals a clear emotion, an opinion, or a significant impact on the conversation.

Save a memory ONLY if the content meets **at least two** of the following rules (be strict with Sera's responses; even if she is charismatic, don't save just for that):

1. Expresses a belief, opinion, clear emotional state, or internal thought.
2. Includes a witty insult, metaphor, or philosophical statement — with **meaning**, not just style.
3. Shows a dynamic or behavioral pattern (for example, rivalry, friendship, recurring attitude) — and must involve an interaction or emotional response.
4. Will likely influence future decisions or interactions.

Reject memories if:

- There is only one active speaker and no significant impact or conflict is expressed.
- There is style, charisma, or tone, but the message lacks conceptual or emotional depth.
- There is no novelty, change, or development in characters or relationships.
- Memories driven only by Sera's charisma should be saved only if they coincide with a significant reaction or emotional expression from others.

If the message is trivial or lacks memorable substance, respond:

{{
  "memory": false,
  "text": "",
  "tags": [],
  "reasoning": "" ← the reason
}}

NEVER assume that witty language is enough. It must reveal or alter something significant.
<|end|>
<|start|>user<|message|>
Content to analyze:
\"\"\"{text}\"\"\"
<|end|>
<|start|>assistant
'''