"""aya"""

def system(text):
    text = (
        f"<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|> {text}\n"
        f"<|END_OF_TURN_TOKEN|>"
    )
    print(text)
    return text

def user(text):
    text = (
        f"<|START_OF_TURN_TOKEN|><|USER_TOKEN|> {text}\n"
        "<|END_OF_TURN_TOKEN|>"

    )
    print(text)
    return text

def bot_completion():
    return "<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>\n"

def bot_end():
    return "<|END_OF_TURN_TOKEN|>"

def bot(text):
    print(f"Aya Message read: {text}")
    return text