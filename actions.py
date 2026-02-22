import re
import math
import random
import discord
from discord.ext import commands
import io
import requests
from PIL import Image, ImageDraw, ImageChops


BONKERS = [
    ("catgirlrisebonk.png", 325, 416, 225),
    ("acvarisebonk.png", 222, 328, 134),
]


class ActionsCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def bot_send(self, ctx, message):
    return await ctx.send("", embed=discord.Embed(description=message))

  async def get_user_from_mention(self, ctx, mention):
    match = re.findall(r"<@!?(\d+)>", mention)
    if not match:
      return mention

    if ctx.guild:
      user = await ctx.guild.fetch_member(int(match[0]))
    else:
      user = await self.bot.fetch_user(int(match[0]))
    return user.display_name

  async def gemini_ask(self, prompt):
    return (await self.bot.gemini.aio.models.generate_content(
        model=self.bot.MODEL_CHEAP, contents=prompt,
    )).text

  async def local_ask(self, prompt):
    response = await self.bot.openai.chat.completions.create(
        model="NOT_USED",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    harmony_marker = "<|channel|>final<|message|>"
    return response[response.index(harmony_marker) + len(harmony_marker):]

  async def do_things_to(self, filename, ctx, *args):
    with open(filename, "rt") as fd:
      THINGS = [lx.strip() for lx in fd.readlines() if lx.strip()]

    author = f"**{ctx.author.display_name}**"
    args = [f"**{await self.get_user_from_mention(ctx, u)}**" for u in args]
    print(f"{filename}: author={author}; args={args}")

    if len(args) == 0:
      msg = random.choice(THINGS + ["No, I will not kiss you"]).format(
          orig=f"**{self.bot.user.name}**", dest=author)

    elif len(args) == 1:
      msg = random.choice(THINGS).format(orig=author, dest=args[0])

    else:
      msg = "\n\n".join(
          random.choice(THINGS).format(orig=author, dest=dest)
          for dest in args)

    await self.bot_send(ctx, msg)

  @commands.command()
  async def hug(self, ctx, *args):
    with open("hug.txt", "rt") as fd:
      HUGS = [lx.strip() for lx in fd.readlines() if lx.strip()]

    GROUP_HUGS = [
        "{subjects} all huddled together.",
        "{subjects} hugged each other pairwise, generating a total of "
        "**{total}** hugs.",
        "{subjects} hugged each other at the same time in the same place "
        "(although I'm not sure how that works with the current "
        "understanding of spacetime).",
    ]

    author = f"**{ctx.author.display_name}**"
    args = [f"**{await self.get_user_from_mention(ctx, u)}**" for u in args]
    print(f"hug: author={author}; args={args}")

    if len(args) >= 2:
      group = [author] + list(args)
      await self.bot_send(ctx, random.choice(GROUP_HUGS).format(
          subjects=", ".join(group),
          total=math.comb(len(group), 2)))
      return

    if len(args) == 0:
      orig = f"**{self.bot.user.name}**"
      dest = author
    else:
      orig = author
      dest = args[0]

    use_ai = random.choice((True, False))
    if use_ai:
      try:
        response = await self.gemini_ask(
            "Can you give me a short line describing a hug that Alex "
            "initiated to Blake? Just return one sentence and nothing "
            "else. Pick a tone at random. The first time either Alex "
            "or Blake is mentioned, use their names instead of "
            "pronouns. Subsequent mentions can use pronouns or names "
            "as needed, and use 'they/them' for both of them."
        )
        msg = response.replace("Alex", orig).replace("Blake", dest)
        await self.bot_send(ctx, msg)
        return
      except Exception:
        pass

    await self.bot_send(ctx, random.choice(HUGS).format(orig=orig, dest=dest))

  @commands.command()
  async def cuddle(self, ctx, target):
    author = f"**{ctx.author.display_name}**"
    dest = f"**{await self.get_user_from_mention(ctx, target)}**"
    print(f"cuddle: author={author}; target={target}")

    # text = await self.local_ask(
    text = await self.gemini_ask(
        "Can you give me a short line describing a Alex cuddling or nuzzling "
        "Blake? Just return one sentence and nothing else. Pick a tone at "
        "random. Use 'they/them' pronouns for both of them instead of gendered "
        "pronouns. Make sure to mention both of them by name at least once in "
        "the sentence, as the reader does not have any prior context."
    )
    msg = text.replace("Alex", author).replace("Blake", dest)
    await self.bot_send(ctx, msg)

  @commands.command()
  async def kiss(self, ctx, *args):
    await self.do_things_to("kiss.txt", ctx, *args)

  @commands.command()
  async def pat(self, ctx, *args):
    await self.do_things_to("pat.txt", ctx, *args)

  @commands.command()
  async def pet(self, ctx, *args):
    await self.do_things_to("pat.txt", ctx, *args)

  @commands.command()
  async def pickup(self, ctx, *args):
    with open("pickup.txt", "rt") as fd:
      PICKUPS = [lx.strip() for lx in fd.readlines() if lx.strip()]

    author = f"**{ctx.message.author.name}**"
    args = [f"**{await self.get_user_from_mention(ctx, u)}**" for u in args]
    print(f"pickup: author={author}; args={args}")

    if len(args) == 0:
      await self.bot_send(ctx, random.choice(PICKUPS))

    elif len(args) == 1:
      await self.bot_send(ctx, f"{author}: {random.choice(PICKUPS)}")

    else:
      await self.bot_send(ctx, f"**{self.bot.user.name}** bonks {author}.")

  @commands.command()
  async def click(self, ctx, *args):
    if not args:
      return
    if not random.choice([True, False, False]):
      return
    args = [f"**{await self.get_user_from_mention(ctx, u)}**" for u in args]
    await self.bot_send(ctx, random.choice([
        f"{args[0]} has become a magical girl!",
        f"{args[0]} has become a cute catgirl!",
        f"{args[0]} has become a blob!",
        "Nothing happened.",
        "..."
    ]))

  @commands.command()
  async def bonk(self, ctx, *args):
    avatar_url = None
    if len(args) == 0 or len(args) > 1:
      avatar_url = ctx.message.author.display_avatar.url
      user = ctx.message.author
    else:
      arg = args[0]
      match = re.findall(r"<@!?(\d+)>", arg.strip())
      if match:
        uid = int(match[0])
        user = await self.bot.fetch_user(uid)
        avatar_url = user.display_avatar.url
      else:
        async for user in ctx.guild.fetch_members(limit=None):
          if user.nick == arg or user.name == arg or str(user.id) == arg:
            avatar_url = user.display_avatar.url
    if not avatar_url:
      return

    background_path, avatarscale, x, y = random.choice(BONKERS)

    res = requests.get(avatar_url)
    img = Image.open(io.BytesIO(res.content)).convert("RGBA")

    size = img.size
    circle_mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(circle_mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    original_alpha = img.getchannel("A")
    combined_mask = ImageChops.multiply(original_alpha, circle_mask)
    img.putalpha(combined_mask)
    img = img.resize((avatarscale, avatarscale), Image.Resampling.LANCZOS)

    background = Image.open(background_path).convert("RGBA")
    background.paste(img, (x, y), img)
    buf = io.BytesIO()
    background.save(buf, format="PNG")
    buf.seek(0)

    file = discord.File(buf, filename="bonk.png")
    emb = discord.Embed(title=f"Rise bonked {str(user)}")
    emb.set_image(url=f"attachment://bonk.png")
    await ctx.send(file=file, embed=emb)

  @commands.command()
  async def askrise(self, ctx, *args):
    msg = "." * random.randint(3, 20)
    return await ctx.reply("", embed=discord.Embed(description=msg))


async def setup(bot):
  await bot.add_cog(ActionsCog(bot))
