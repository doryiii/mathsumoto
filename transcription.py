import discord
from discord.ext import commands, voice_recv
from discord.ext.voice_recv.extras.speechrecognition import SpeechRecognitionSink
import speech_recognition as sr
from speech_recognition.recognizers.whisper_api.openai import OpenAICompatibleRecognizer
import openai
import db


class TranscriptionCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.ignored_users = {}
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

    guild_id = ctx.guild.id if ctx.guild else None
    self.ignored_users[(ctx.channel.id, guild_id)] = db.get_ignored_users(
      ctx.channel.id, guild_id)

    def text_callback(user, text):
      if text and text.strip():
        ctx.bot.loop.create_task(ctx.send(f"**{user.name}**: {text}"))

    def process_callback(recognizer, audio, user):
      if not audio.frame_data:
        return None
      if getattr(user, 'bot', False):
        return None
      if user.id in self.ignored_users.get((ctx.channel.id, guild_id), set()):
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

  @commands.command()
  async def ignoreme(self, ctx):
    guild_id = ctx.guild.id if ctx.guild else None
    key = (ctx.channel.id, guild_id)
    if key not in self.ignored_users:
      self.ignored_users[key] = db.get_ignored_users(ctx.channel.id, guild_id)
    self.ignored_users[key].add(ctx.author.id)
    db.add_ignored_user(ctx.channel.id, guild_id, ctx.author.id)
    await ctx.send(f"Okay, I will ignore your voice in this channel, {ctx.author.mention}.")

  @commands.command()
  async def unignoreme(self, ctx):
    guild_id = ctx.guild.id if ctx.guild else None
    key = (ctx.channel.id, guild_id)
    if key not in self.ignored_users:
      self.ignored_users[key] = db.get_ignored_users(ctx.channel.id, guild_id)
    self.ignored_users[key].discard(ctx.author.id)
    db.remove_ignored_user(ctx.channel.id, guild_id, ctx.author.id)
    await ctx.send(f"I will listen to your voice again in this channel, {ctx.author.mention}.")

  @commands.command()
  async def ignoredusers(self, ctx):
    guild_id = ctx.guild.id if ctx.guild else None
    users = db.get_ignored_users(ctx.channel.id, guild_id)
    if not users:
      await ctx.send("No users are currently being ignored in this channel.")
      return
    mentions = ", ".join(f"<@{u}>" for u in users)
    await ctx.send(f"Currently ignored users in this channel: {mentions}")

  @commands.command(aliases=["bye", "stop"])
  async def stoptranscribe(self, ctx):
    if not ctx.voice_client:
      return
    ctx.voice_client.stop()
    await ctx.voice_client.disconnect()
    await ctx.send("Bye~")


async def setup(bot):
  await bot.add_cog(TranscriptionCog(bot))
