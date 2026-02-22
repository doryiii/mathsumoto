import argparse
from openai import AsyncOpenAI
from google import genai
from discord.ext import commands
import discord
import subprocess
import tempfile
import re
import random
import math
import os


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(".", case_insensitive=True, intents=intents)


async def setup_hook():
  await bot.load_extension("wolfram")
  await bot.load_extension("xkcd")
  await bot.load_extension("actions")
  await bot.load_extension("images")
  await bot.load_extension("aoi")
  await bot.load_extension("info")
  await bot.load_extension("chat")
  await bot.load_extension("transcription")

bot.setup_hook = setup_hook


@bot.event
async def on_ready():
  bot.discord_id = bot.user.mention
  await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.listening, name="...")
  )
  print(f"{bot.user} has connected to Discord! (ID: {bot.discord_id})")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Run the Matsumoto Discord bot.")
  parser.add_argument(
    "--discord-token", required=True, help="Discord bot token"
  )
  parser.add_argument(
    "--gemini-api-key", required=True, help="Gemini API key"
  )
  parser.add_argument(
    "--wolfram-alpha-app-id", required=True, help="Wolfram Alpha App ID"
  )
  parser.add_argument(
    "--openai-base-url", required=True, help="OpenAI-compatible base URL"
  )
  parser.add_argument(
    "--openai-api-key", default="NOT_USED", help="OpenAI API key (optional)"
  )
  parser.add_argument(
    "--whisper-base-url", required=True, help="Whisper API compatible base URL"
  )
  parser.add_argument(
    "--whisper-api-key", default="NOT_USED", help="Whisper API key (optional)"
  )
  args = parser.parse_args()

  bot.WOLFRAM_ALPHA_APP_ID = args.wolfram_alpha_app_id

  bot.gemini = genai.Client(api_key=args.gemini_api_key)
  bot.MODEL_MAIN = "gemini-3-flash-preview"
  bot.MODEL_CHEAP = "gemini-3-flash-preview"

  bot.openai = AsyncOpenAI(
      api_key=args.openai_api_key,
      base_url=args.openai_base_url,
  )

  bot.WHISPER_URL = args.whisper_base_url
  bot.WHISPER_KEY = args.whisper_api_key

  bot.run(args.discord_token)
