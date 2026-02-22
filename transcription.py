import discord
from discord.ext import commands, voice_recv
from discord.ext.voice_recv.extras.speechrecognition import SpeechRecognitionSink
import speech_recognition as sr
from speech_recognition.recognizers.whisper_api.openai import OpenAICompatibleRecognizer
import openai


class TranscriptionCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.openai_client = openai.OpenAI(
        api_key=self.bot.WHISPER_KEY,
        base_url=self.bot.WHISPER_URL
    )
    self.whisper_recognizer = OpenAICompatibleRecognizer(self.openai_client)

  @commands.command()
  async def transcribe(self, ctx):
    if not ctx.author.voice:
      await ctx.send(f"{ctx.author.name} is not in a voice channel.")
      return

    def text_callback(user, text):
      if text and text.strip():
        ctx.bot.loop.create_task(ctx.send(f"**{user.name}**: {text}"))

    def process_callback(recognizer, audio, user):
      if not audio.frame_data:
        return None
      try:
        return self.whisper_recognizer.recognize(audio, model="notneeded")
      except Exception as e:
        print(f"Error recognizing speech for {user.name}: {e}")
        return None

    try:
      vc = await ctx.author.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
    except discord.errors.ClientException:
      # Already connected to a voice channel
      vc = ctx.voice_client
      if type(vc) is not voice_recv.VoiceRecvClient:
        await ctx.send("Voice client is not VoiceRecvClient. Please disconnect and try again.")
        return

    sink = SpeechRecognitionSink(
        process_cb=process_callback,
        text_cb=text_callback,
        phrase_time_limit=60,
        ignore_silence_packets=True,
    )

    # Increase pause_threshold to avoid splitting sentences too early
    old_factory = sink._stream_data.default_factory

    def custom_factory():
      data = old_factory()
      data['recognizer'].pause_threshold = 2.0
      return data
    sink._stream_data.default_factory = custom_factory

    vc.listen(sink)
    await ctx.send(f"Listening to #{ctx.author.voice.channel.name}...")

  @commands.command(aliases=["bye", "stop"])
  async def stoptranscribe(self, ctx):
    if not ctx.voice_client:
      return
    ctx.voice_client.stop()
    await ctx.voice_client.disconnect()
    await ctx.send("Bye~")


async def setup(bot):
  await bot.add_cog(TranscriptionCog(bot))
