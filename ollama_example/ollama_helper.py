import subprocess
import base64
import json
import re
import os
import time
import shutil

try:
    from openai import OpenAI as _OpenAIClient
    _BACKEND = 'openai'
except ImportError:
    import ollama as _ollama
    _BACKEND = 'ollama'

SYSTEM_PROMPT = """You are PiCar-X, a friendly small robot car assistant.
Respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):
{"actions": ["action1"], "answer": "Your spoken response here"}

Available actions (use an empty list if none apply):
"shake head", "nod", "wave hands", "resist", "act cute", "rub hands",
"think", "twist body", "celebrate", "depressed", "honking", "start engine", "stop"

Rules:
- Always include "answer" with what you want to say out loud
- Keep answers concise and friendly
- Choose actions that match your emotional response
- Output raw JSON only — no code fences, no explanation"""


def chat_print(label, message):
    print(f'{time.time():.3f} {label:>6} >>> {message}')


def _parse_response(text):
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except Exception:
        try:
            return eval(text)
        except Exception:
            return str(text)


class OllamaHelper:
    def __init__(self, host, model, vision_model, assistant_name='picarx'):
        self.host = host
        self.model = model
        self.vision_model = vision_model
        self.assistant_name = assistant_name
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if _BACKEND == 'openai':
            # llama.cpp server (or any OpenAI-compatible endpoint)
            self.client = _OpenAIClient(base_url=f"{host}/v1", api_key="none")
            self._chat = self._chat_openai
        else:
            # native Ollama
            self.client = _ollama.Client(host=host)
            self._chat = self._chat_ollama

    def _chat_openai(self, messages, model):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    def _chat_ollama(self, messages, model):
        response = self.client.chat(model=model, messages=messages)
        return response.message.content

    def stt(self, audio, language=None):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            lang = 'en-US'
            if isinstance(language, list) and len(language) > 0:
                lang = language[0]
            elif isinstance(language, str) and language:
                lang = language
            return recognizer.recognize_google(audio, language=lang)
        except Exception as e:
            if 'UnknownValueError' in type(e).__name__:
                return False
            print(f"stt err: {e}")
            return False

    def dialogue(self, msg):
        chat_print("user", msg)
        self.messages.append({"role": "user", "content": msg})

        value = self._chat(self.messages, self.model)
        self.messages.append({"role": "assistant", "content": value})
        chat_print(self.assistant_name, value)
        return _parse_response(value)

    def dialogue_with_img(self, msg, img_path):
        chat_print("user", msg)

        with open(img_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        if _BACKEND == 'openai':
            img_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": msg},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}},
                ],
            }
        else:
            img_message = {"role": "user", "content": msg, "images": [img_data]}

        messages = self.messages + [img_message]
        value = self._chat(messages, self.vision_model)
        self.messages.append({"role": "user", "content": msg})
        self.messages.append({"role": "assistant", "content": value})
        chat_print(self.assistant_name, value)
        return _parse_response(value)

    def text_to_speech(self, text, output_file, voice='en', response_format='wav', speed=1, instructions=''):
        try:
            dir_path = os.path.dirname(output_file)
            if dir_path and not os.path.exists(dir_path):
                os.mkdir(dir_path)

            speed_wpm = int(175 * speed)
            cmd = ['espeak-ng', '-v', voice, '-s', str(speed_wpm), '-w', output_file, text]
            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                return True
            print(f'tts err: {result.stderr.decode()}')
            return False
        except Exception as e:
            print(f'tts err: {e}')
            return False
