# voice.py
import threading
import queue
import numpy as np
import pyaudio
import time
import json
from faster_whisper import WhisperModel

NEON_GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

# TODO add finish log all conversation

class Voice:
    def __init__(self, model_size="small", language="es", file_path="log.txt"):
        self.name = "RealTimeTranscriber"
        self.language = language
        self.file_path = file_path
        self.is_running = False  # To manage the state of the threads

        print("Loading Whisper model...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1024)
        
        self.q = queue.Queue()
        self.accumulated = []
        print("Starting voice recognition...")
        self.lock = True

    def transcribe_chunk(self, audio_bytes):
        audio_np = np.frombuffer(audio_bytes, np.int16).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(
            audio_np, 
            language=self.language,
            beam_size=5, 
            vad_filter=True
        )
        return " ".join([seg.text for seg in segments]).strip()

    def audio_producer(self, chunk_size=32000, overlap=8000):
        last = b""
        while self.is_running: #flag to control the loop
            data = self.stream.read(chunk_size - overlap, exception_on_overflow=False)
            self.q.put(last + data)
            last = data[-overlap:]


    def audio_consumer(self):
        current_sentence = []
        last_speech_time = time.time()
        SILENCE_THRESHOLD = 2.0

        while self.is_running:
            try:
                audio_bytes = self.q.get(timeout=1)
                transcription = self.transcribe_chunk(audio_bytes)

                if transcription:
                    current_sentence.append(transcription)
                    last_speech_time = time.time()
                    print(NEON_GREEN + " ".join(current_sentence) + "..." + RESET_COLOR, end='\r', flush=True)

                elif current_sentence:
                    if time.time() - last_speech_time > SILENCE_THRESHOLD and self.lock:
                        self.lock = False
                        
                        final_sentence = " ".join(current_sentence)
                        print("\n" + NEON_GREEN + "Frase final: " + final_sentence + RESET_COLOR)


                        # Joins all accumulated sentences
                        full_conversation = " ".join(self.accumulated)

                        data_to_write = [
                            {
                                "User": final_sentence # Use actual sentence
                            }
                        ]
                        try:
                            with open(self.file_path, "w", encoding="utf-8") as f:
                                json.dump(data_to_write, f, ensure_ascii=False, indent=4)
                        except Exception as e:
                            print(f"Error to write in file: {e}")

                        current_sentence = []
                        print("Listening...")
            except queue.Empty:
                continue
    
    def lock(self):
        """Blocks saving the final sentence to the file."""
        print("\n[!] Blocking saving of sentences.")
        self.lock = False

    def unlock(self):
        """Unblocks saving the final sentence to the file."""
        print("\n[!] Unblocking saving of sentences.")
        self.lock = True
    
    def start(self):
        """Starts the audio production and consumption threads."""
        if self.is_running:
            print("Already running.")
            return

        print("Starting listening threads...")
        self.is_running = True
        self.thread_prod = threading.Thread(target=self.audio_producer, daemon=True)
        self.thread_cons = threading.Thread(target=self.audio_consumer, daemon=True)
        self.thread_prod.start()
        self.thread_cons.start()
        print("Listening...")

    def stop(self):
        """Stops the audio threads and releases resources."""
        if not self.is_running:
            return

        print("\nStopping...")
        self.is_running = False

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
        with open(self.file_path, "w") as f:
            f.write(" ".join(self.accumulated))
        
        print("LOG:" + " ".join(self.accumulated))
        print("Resources released.")

# Just for individual testing
if __name__ == "__main__":
    recognizer = Voice(model_size="small")
    recognizer.start()
    try:
        time.sleep(10) 
        print("\n--- stopping ---")
        recognizer.lock()
        time.sleep(10)
        print("\n--- unlocking ---")
        recognizer.unlock()
        
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        recognizer.stop()