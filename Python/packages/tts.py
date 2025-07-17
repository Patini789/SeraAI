import os
import edge_tts
import pygame

class TTS:
    def __init__(self, rate="+10%", pitch="-10Hz", voice="es-HN-KarlaNeural"):
        self.rate = rate
        self.pitch = pitch
        self.voice = voice

    async def speak(self, text):
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

        pygame.mixer.init()
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.quit()

        if os.path.exists("output.mp3"):
            os.remove("output.mp3")

    def start(self):
        """Placeholder method for device initialization."""
        pass
