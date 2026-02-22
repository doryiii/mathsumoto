import discord
from discord.ext import commands
import httpx
import nekos


class ImagesCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def neko(self, ctx, *args):
    msg = discord.Embed()
    msg.set_image(url=nekos.img("neko"))
    return await ctx.send("", embed=msg)

  @commands.command()
  async def inu(self, ctx, *args):
    URL = ("https://danbooru.donmai.us/posts/random.json?login=jimreynold2nd"
           "&api_key=ufrjwL3CPumb9dB3XtUEGT6r"
           "&tags=rating%3Ageneral+dog_girl"
           "+-comic+-greyscale+-furry+-absolutely_everyone")
    HEADERS = {"User-Agent": "curl/7.86.0"}
    async with httpx.AsyncClient() as http:
      img_url = (await http.get(URL, headers=HEADERS)).json()["file_url"]
    print("Inu URL: " + img_url)
    msg = discord.Embed()
    msg.set_image(url=img_url)
    return await ctx.send("", embed=msg)

  @commands.command()
  async def usagi(self, ctx, *args):
    URL = ("https://danbooru.donmai.us/posts/random.json?login=jimreynold2nd"
           "&api_key=ufrjwL3CPumb9dB3XtUEGT6r"
           "&tags=rating%3Ageneral+rabbit_ears"
           "+-comic+-greyscale+-furry+-absolutely_everyone")
    HEADERS = {"User-Agent": "curl/7.86.0"}
    async with httpx.AsyncClient() as http:
      img_url = (await http.get(URL, headers=HEADERS)).json()["file_url"]
    print("Inu URL: " + img_url)
    msg = discord.Embed()
    msg.set_image(url=img_url)
    return await ctx.send("", embed=msg)

  @commands.command()
  async def catboy(self, ctx, *args):
    URL = ("https://danbooru.donmai.us/posts/random.json?login=jimreynold2nd"
           "&api_key=ufrjwL3CPumb9dB3XtUEGT6r"
           "&tags=rating%3Asafe%20catboy%201boy%20-comic%20-condom"
           "%20-furry%20-large_pectorals")
    HEADERS = {"User-Agent": "curl/7.86.0"}
    async with httpx.AsyncClient() as http:
      img_url = (await http.get(URL, headers=HEADERS)).json()["file_url"]
    print("Catboy URL: " + img_url)
    msg = discord.Embed()
    msg.set_image(url=img_url)
    return await ctx.send("", embed=msg)


async def setup(bot):
  await bot.add_cog(ImagesCog(bot))
