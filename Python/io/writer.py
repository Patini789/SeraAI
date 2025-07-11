"""Manage current_conversation.json """

import requests

class Writer:
    def __init__(self, url, model):
        self.url = url
        self.model = model

    def send(self, message):
        payload = {
            "model": self.model,
            "prompt": message,
            "max_tokens": 1024,
            "temperature": 0.3,
            "top_p": 0.4
        }

        try:
            response = requests.post(self.url, json=payload, timeout=400)
            response.raise_for_status()

            result = response.json()
            choices = result.get("choices", [])
            if choices and choices[0].get("text"):
                generated_text = choices[0]["text"].strip()
                print("✅ Texto generado:", generated_text)
                return generated_text
            else:
                print("⚠️ No se encontraron resultados válidos.")
                return ""

        except requests.exceptions.Timeout:
            print("❌ Error: El modelo tardó demasiado en responder (timeout).")
            return "Error: timeout"
        except requests.RequestException as e:
            print(f"❌ Error al contactar el modelo: {e}")
            return "Error: request failed"


