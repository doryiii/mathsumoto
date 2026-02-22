import requests
import discord
from discord.ext import commands


class XkcdCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def xkcd(self, ctx, *args):
    async with ctx.typing():
      comics = requests.post(
          "http://localhost:9523", " ".join(args)).json()
      comic = comics[0]
      alternates = comics[1:]
      msg = discord.Embed(
          title=comic["title"],
          url=f"https://xkcd.com/{comic['id']}",
          description=comic["alt"] if "alt" in comic else "",
      )
      score = f"{comic['score']:.4f}" if "score" in comic else ""
      alts = "\n".join([
          f"https://xkcd.com/{a['id']} {a['title']} ({a['score']:.4f})"
          for a in alternates if a['score'] >= 0.4
      ])
      msg.set_footer(
        text=f"cosine: {score}{'\n\nSee also:\n' if alts else ''}{alts}")
      msg.set_image(url=comic["img"])
      return await ctx.reply("", embed=msg)


async def setup(bot):
  await bot.add_cog(XkcdCog(bot))
