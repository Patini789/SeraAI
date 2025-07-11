"""Look current_conversarion.json and notice changes. Send events. """

import os
import json
import time
import threading

class Reader:
    def __init__(self, file_path, on_new_message_fn, interval=3):
        self.file_path = file_path #current_conversation.json
        self.on_new_message_fn = on_new_message_fn #new message function
        self.interval = interval #interval in seconds
        self._running = False
        self._thread = None

        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            print("[Reader] File not found creating new file")
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding= "utf-8") as f:
                json.dump([], f, indent=4)
        else:
            print("[Reader] File exists")

    def _log(self, msg):
        print(f"[Reader.log] {msg}")

    def _read_loop(self):
        while self._running:
            if not os.path.exists(self.file_path):
                self._log("File not found")
                time.sleep(1)
                continue
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    self._log("Invalid format")
                    time.sleep(1)
                    continue

            except json.JSONDecodeError:
                self._log("Error decoding JSON")
                time.sleep(1)
                continue

            except Exception as e:
                self._log(f"Unexpected error: {e}")
                time.sleep(1)
                continue

            updated_data = []
            updated = False

            for item in data:
                if item.get("User") != "":
                    self._log("Sending conversation...")
                    self._log(item)
                    item["User"] = ""
                    try:
                        self.on_new_message_fn(item)
                    except Exception as e:
                        self._log(f"Error in on_new_message_fn {e}")
                    updated = True
                else:
                    updated_data.append(item)

            if updated:
                try:
                    with open(self.file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    self._log("Updated")
                except Exception as e:
                    self._log(f"Error in save {e}")
            time.sleep(self.interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        self._log("Reader started")

    def stop(self):
        self._running = False
        self._log("Reader stopped")