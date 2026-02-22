# Mathsumoto

Mathsumoto is a feature-rich, modular Discord bot written in Python using `discord.py`. It integrates with Google's GenAI (Gemini) for intelligent, persona-driven conversations, handles voice transcription via Whisper, queries Wolfram Alpha, and provides a host of fun social and image generation commands.

## Features

### Wolfram Alpha Integration
*   **`.domath <query>`**: Queries the Wolfram Alpha API to solve math problems, answer science questions. Can return plots and graphs as image attachments.

### Live Voice Transcription
*   **`.transcribe`**: The bot joins your current voice channel and listens. It uses an OpenAI-compatible Whisper API endpoint to transcribe spoken audio into text in real-time and posts it to the text channel.
*   **`.stoptranscribe`** (Aliases: `.bye`, `.byee`, `.stop`): Disconnects the bot from the voice channel and stops listening.

### Image & Comic Fetching
*   **`.xkcd <query>`**: Searches for and retrieves XKCD comics (requires a local search service).
*   **Anime Image Fetching**:
    *   **`.neko`**: Posts a random catgirl image.
    *   **`.inu`**: Posts a random doggirl image from Danbooru.
    *   **`.usagi`**: Posts a random bunnygirl image from Danbooru.
    *   **`.catboy`**: Posts a random catboy image from Danbooru.

### Aoi Custom Image Generator
Generates custom text bubbles over images of "Aoi" using a local Scribus script via XVFB.
*   **`.aoi`**: Posts a random Aoi image.
*   **`.aoisay <text>`**, **`.aoiyell <text>`**, **`.aoitsun <text>`**, **`.aoithink <text>`**, **`.aoiwave <text>`**, **`.aoiexcite <text>`**, **`.aoiwhisper <text>`**, **`.aoieat <text>`**, **`.aoiheart <text>`**: Renders your custom text onto an image with the corresponding mood.

### Social & Roleplay Actions
Interact with other users using dynamic, sometimes AI-generated, flavor text!
*   **`.hug [@user]`**: Hugs a user. Sometimes utilizes Gemini to generate a unique, narrative description of the hug. Also supports group hugs!
*   **`.cuddle [@user]`**: Cuddles a user, utilizing Gemini for dynamic text generation.
*   **`.kiss [@user]`**, **`.pat [@user]`**, **`.pet [@user]`**: Standard roleplay interactions.
*   **`.pickup [@user]`**: Delivers a random pickup line.
*   **`.bonk [@user]`**: Generates an image of the target user's avatar getting "bonked" and posts it to the channel.
*   **`.click [@user]`**: Magically transforms the target user into something else.

### Utility
*   **`.avatar [@user]`**: Fetches and displays the full-resolution avatar of the mentioned user(s) or yourself.

### Intelligent Chat (Gemini)
*   **Persona-Driven Conversations:** The bot responds to mentions and adopts different personas (e.g., standard Rise, Shy Smart Rise, or Aoi) depending on the specific server and channel it is interacting in.
*   **Multimodal Support:** You can attach images to your messages, and the bot will process them inline using the Gemini Vision capabilities.
*   **Persistent Memory:** Conversations are tracked per-channel and persisted locally in a SQLite database (`convo.db`), allowing the bot to remember context even after restarts.
*   **`.newchat [context]`**: Clears the current channel's conversation history to start fresh. You can optionally provide a custom system prompt/context.

---

## Setup & Running

Mathsumoto uses `argparse` to handle secrets via command-line arguments rather than hardcoding them.

### Prerequisites
*   Python 3.10+
*   `discord.py`
*   `google-genai`
*   `openai`
*   `SpeechRecognition`
*   `discord-ext-voice-recv`
*   `Pillow` (PIL)
*   `xmltodict`
*   `httpx`
*   A running instance of Xvfb and Scribus (for `.aoi*` text rendering).
*   A running XKCD search service (for the `.xkcd` command).

### Starting the Bot

Run `mathsumoto.py` and provide the required API keys and URLs:

```bash
python3 mathsumoto.py 
    --discord-token "YOUR_DISCORD_BOT_TOKEN" 
    --gemini-api-key "YOUR_GEMINI_API_KEY" 
    --whisper-base-url "http://localhost:8000/v1/" 
```

