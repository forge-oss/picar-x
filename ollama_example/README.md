# PiCar-X Ollama Example

Run PiCar-X with a local LLM via [Ollama](https://ollama.com) — no API key required.

----------------------------------------------------------------

## Install dependencies

- Make sure you have installed PiCar-X and related dependencies first

    <https://docs.sunfounder.com/projects/picar-x-v20/en/latest/python/python_start/install_all_modules.html>

- Install Ollama on the host machine (Pi or PC)

    <https://ollama.com/download>

- Install Python dependencies and system packages

> [!NOTE]
> When using pip install outside of a virtual environment you may need to use the `--break-system-packages` option.

        sudo pip3 install ollama SpeechRecognition --break-system-packages

        sudo apt install python3-pyaudio
        sudo apt install sox espeak-ng
        sudo pip3 install -U sox --break-system-packages

----------------------------------------------------------------

## Pull Ollama models

    # Chat model (text only)
    ollama pull llama3.2

    # Vision model (required for image analysis, --no-img to skip)
    ollama pull llava

You can use any compatible models — update `OLLAMA_MODEL` and `OLLAMA_VISION_MODEL` in `ollama_config.py` to match.

----------------------------------------------------------------

## Configure

Edit `ollama_config.py`:

    OLLAMA_HOST = "http://localhost:11434"  # change if Ollama runs on another machine
    OLLAMA_MODEL = "llama3.2"              # any chat model you have pulled
    OLLAMA_VISION_MODEL = "llava"          # multimodal model for image analysis

----------------------------------------------------------------

## Run

- Run with voice input

        sudo python3 gpt_car.py

- Run with keyboard input

        sudo python3 gpt_car.py --keyboard

- Run without image analysis (text-only model is sufficient)

        sudo python3 gpt_car.py --keyboard --no-img

> [!WARNING]
> Run with `sudo`, otherwise there may be no sound from the speaker.
> For certain Robot HATs, you might need to enable the speaker with `"pinctrl set 20 op dh"` or `"robot-hat enable_speaker"`.

----------------------------------------------------------------

## Modify parameters [optional]

- **STT language** — set `LANGUAGE` in `gpt_car.py` to improve accuracy and latency.
  `LANGUAGE = []` uses the default (`en-US`). Example: `LANGUAGE = ['zh']` for Chinese.

- **TTS volume gain** — set `VOLUME_DB` in `gpt_car.py`. Keep it at or below `5` to avoid distortion.

- **TTS voice** — set `TTS_VOICE` in `gpt_car.py` to any `espeak-ng` voice.
  Run `espeak-ng --voices` to list available voices. Common options: `en`, `en-us`, `en-gb`, `zh`.

- **Chat / vision model** — update `OLLAMA_MODEL` / `OLLAMA_VISION_MODEL` in `ollama_config.py`.

- **System prompt** — edit `SYSTEM_PROMPT` in `ollama_helper.py` to change the robot's personality.

----------------------------------------------------------------

## Preset actions

`preset_actions.py` contains preset actions such as `shake_head`, `nod`, `depressed`, `honking`, `start_engine`, etc.
Run it standalone to preview all actions:

    python3 preset_actions.py
