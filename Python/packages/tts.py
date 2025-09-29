import os
import edge_tts
import pygame
import json

class TTS:
    def __init__(self, rate="+10%", pitch="-10Hz", voice="es-HN-KarlaNeural", emotion_path=""):
        self.rate = rate
        self.pitch = pitch
        self.voice = voice
        self.emotion_path = emotion_path

    async def speak(self, text, voice_instance):
        """Converts text to speech using Edge. TTS and plays the audio."""
        if os.path.exists("output.mp3"):
            os.remove("output.mp3")

        communicate = edge_tts.Communicate(
            text,
            voice=self.voice,  # Example: gl-ES-SabelaNeural
            rate=self.rate,
            pitch=self.pitch
        )
        await communicate.save("output.mp3")

        self.set_talking(True)

        pygame.mixer.init()
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.quit()

        if os.path.exists("output.mp3"):
            os.remove("output.mp3")
        self.set_talking(False)
        if voice_instance:
            voice_instance.unlock()

    def set_talking(self, state: bool):
        """Upgrade field 'talking' from current_emotion.json"""
        if not self.emotion_path or not os.path.exists(self.emotion_path):
            return

        try:
            with open(self.emotion_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}

        data["talking"] = state

        with open(self.emotion_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def start(self):
        """Placeholder method for device initialization."""
        pass
