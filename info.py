import re
import discord
from discord.ext import commands


class InfoCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def avatar(self, ctx, *args):
    avatars = {}

    if len(args) == 0:
      avatars[str(ctx.message.author)] = ctx.message.author.display_avatar.url

    for arg in args:
      # a mention
      match = re.findall(r"<@!?(\d+)>", arg.strip())
      if match:
        uid = int(match[0])
        user = await ctx.bot.fetch_user(uid)
        avatars[str(user)] = user.display_avatar.url

      # a simple name string
      else:
        async for user in ctx.guild.fetch_members(limit=None):
          if user.nick == arg or user.name == arg or str(user.id) == arg:
            avatars[user] = user.display_avatar.url

    if not avatars:
      return

    for user in avatars:
      em = discord.Embed(title=str(user))
      em.set_image(url=avatars[user])
      await ctx.send(embed=em)


async def setup(bot):
  await bot.add_cog(InfoCog(bot))
