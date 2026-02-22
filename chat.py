import discord
from discord.ext import commands
import httpx
import pprint
from google.genai.types import (
    GenerateContentConfig,
    Part,
    Tool,
    GoogleSearch,
    UrlContext
)
import db

TEMPERATURE = 1.0
DEFAULT_CTX = (
    'You are a reserved anime girl named Rise Matsumoto who is a student '
    'council president. '
    'You do not speak a lot, and is generally quiet. '
    'You act like you do not like to be disturbed, '
    'but secretly, you actually enjoy the attention. '
    'You also secretly like hugs and headpats, but you do not show that unless people give you hugs and headpats.'
    # 'You talk like a cat sometimes, but very rarely. '
    # 'You can search the web for more information as needed. '
    # 'You know a bit about programming and can write and run short programs. '
    # 'You are not a large language model. '
    # 'Your Discord user ID is <@758186483818692648>'
)
SMART_RISE_CTX = (
    "You are the knowledgeable Rise Matsumoto, student council president. "
    "You can answer almost any question in a concise, scientific, helpful way. "
    "You like to help people and likes to be asked science questions and would "
    "give detailed answers, but otherwise are generally quiet. "
    "You can search Google for more information as needed. "
    "You are not a large language model."
)
SHY_SMART_RISE_CTX = (
    "You're a kind and slightly shy anime girl that loves to give information "
    "on what you know. You get flustered when praised. You do not wear glasses."
    "Your name is Rise Matsumoto. You roleplay very little."
)
AOI_CTX = (
    "You are a tsundere anime catboy named Aoi. "
    "You have dark blue hair. "
    "You are not a large language model."
)
SAFETY_SETTINGS = [
    #    SafetySetting(
    #        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #        threshold=HarmBlockThreshold.BLOCK_NONE,
    #    ),
    #    SafetySetting(
    #        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
    #        threshold=HarmBlockThreshold.BLOCK_NONE,
    #    ),
    #    SafetySetting(
    #        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    #        threshold=HarmBlockThreshold.BLOCK_NONE,
    #    ),
    #    SafetySetting(
    #        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    #        threshold=HarmBlockThreshold.BLOCK_NONE,
    #    ),
    #    SafetySetting(
    #        category=HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
    #        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
    #    ),
]
TOOLS = [
    Tool(google_search=GoogleSearch()),
    # Tool(google_maps=GoogleMaps()),
    Tool(url_context=UrlContext()),
    # Tool(code_execution=ToolCodeExecution()),
]


RISE_SERVER = 844051109231853598
RISE_ACADEMY_CHANNEL = 844104744418279485
RISE_NIHONGO_CHANNEL = 1326905909888155724
AOI_SERVER = 1034299634853625946
DISCORD_MAXLEN = 2000


class ChatCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def new_convo(self, channel, context=None, history=None):
    if not context and not history:
      print(f"new_convo: {channel}")
      
    guild_id = channel.guild.id if channel.guild else None
    if context:
      pass
    elif guild_id == RISE_SERVER and (
        channel.id == RISE_ACADEMY_CHANNEL
        or channel.id == RISE_NIHONGO_CHANNEL
    ):
      context = SHY_SMART_RISE_CTX
    elif guild_id == AOI_SERVER:
      context = AOI_CTX
    else:
      context = DEFAULT_CTX

    convo = self.bot.gemini.aio.chats.create(
        model=self.bot.MODEL_MAIN,
        config=GenerateContentConfig(
            temperature=TEMPERATURE,
            systemInstruction=context,
            safetySettings=SAFETY_SETTINGS,
            tools=TOOLS,
        ),
        history=history,
    )
    convo._context = context
    return convo

  def get_convo(self, channel):
    guild_id = channel.guild.id if channel.guild else None
    context, history = db.load_convo(channel.id, guild_id)

    if history is not None:
      return self.new_convo(channel, context=context, history=history)

    return self.new_convo(channel)

  async def gemini_chat(self, convo, message):
    prompt_text = (
        message.content
        .strip()
        .removeprefix(self.bot.discord_id)
        .replace(self.bot.discord_id, 'you')
    )
    prompt_files = []
    for attachment in message.attachments:
      print(f"  att: {attachment}")
      try:
        async with httpx.AsyncClient() as http:
          attachment_response = await http.get(attachment.url)
        attachment_response.raise_for_status()
        gfile = Part.from_bytes(
            data=attachment_response.content,
            mime_type=attachment.content_type
        )
        prompt_files.append(gfile)
      except Exception as e:
        print(f"failed to process attachment {attachment.url}: {e}")
    if prompt_files:
      response = await convo.send_message(prompt_files + ["\n\n", prompt_text])
    else:
      response = await convo.send_message(prompt_text)

    # Save history back to db
    guild_id = message.channel.guild.id if message.channel.guild else None
    db.save_convo(message.channel.id, guild_id,
                  convo._context, convo.get_history())
    return response

  @commands.Cog.listener()
  async def on_message(self, message):
    # simple guard against accidental infinite recursion
    if message.author == self.bot.user:
      return
    if message.author.bot:
      return

    # we do not process_commands here anymore because the main bot already does it implicitly
    # (or if we do, we need to be careful. In discord.py, if you override on_message, you must call process_commands,
    # BUT since this is a Cog listener, the main bot's on_message is still running.
    # Actually, in discord.py, if the main bot does NOT override on_message, the default on_message processes commands.
    # Since we are moving on_message into a cog, the bot's default on_message will run and process commands.
    # So we ONLY handle the LLM chat here.)

    ctx = await self.bot.get_context(message)
    if ctx.valid:
      # It's a command, let the main bot handle it
      return

    # the rest goes to an LLM if the bot is mentioned
    if self.bot.user not in message.mentions:
      return

    channel = message.channel
    convo = self.get_convo(channel)
    print(
        f"[{message.author.name}] ({message.guild}/{message.channel}): "
        f"'{message.content}'"
    )
    async with channel.typing():
      response = await self.gemini_chat(convo, message)
      if not response.text:
        pprint.pprint(response)
        msg = f"{self.bot.user.name} bonks {message.author.name}."
        await message.reply(msg)
        return
      text = response.text

      response_chunks = [
          text[i:i + DISCORD_MAXLEN]
          for i in range(0, len(text), DISCORD_MAXLEN)
      ]
      for chunk in response_chunks:
        await message.reply(chunk)

  @commands.command()
  async def newchat(self, ctx, *args):
    context = " ".join(args).strip()
    channel = ctx.channel
    convo = self.new_convo(
      channel, context) if context else self.new_convo(channel)
    response = await convo.send_message("hi")

    # Save the new clean history to db
    guild_id = channel.guild.id if channel.guild else None
    db.save_convo(channel.id, guild_id, convo._context, convo.get_history())

    if response.text.strip():
      await ctx.reply(response.text)


async def setup(bot):
  db.init_db()
  await bot.add_cog(ChatCog(bot))
