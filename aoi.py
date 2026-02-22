import os
import random
import tempfile
import subprocess
import pprint
import discord
from discord.ext import commands


class AoiCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def scribus(self, subdir, message, outname):
    print(f"{subdir}: {message}")
    sla_files = [f for f in os.listdir(subdir) if f.endswith(".sla")]
    infile = os.path.join(subdir, random.choice(sla_files))
    with tempfile.TemporaryDirectory() as tmpdirname:
      outfile = os.path.join(tmpdirname, outname)
      cmd = ["xvfb-run", "--auto-display",
             "scribus", "--no-gui", "--no-splash", "--python-script",
             "scribus.py", message, outfile, "--", infile]
      print(cmd)
      p = subprocess.run(cmd, check=True, capture_output=True,
                         env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
      pprint.pprint(p)
      return discord.File(outfile, outname)

  @commands.command()
  async def aoi(self, ctx, *args):
    files = [f for f in os.listdir("aoi")
             if f.endswith(".png") or f.endswith(".jpg")]
    infile = os.path.join("aoi", random.choice(files))
    await ctx.send("", files=[discord.File(infile, "aoi.png")])

  @commands.command()
  async def aoiyell(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else ""
    await ctx.send("", files=[self.scribus("aoiyell", message, "aoi.png")])

  @commands.command()
  async def aoitsun(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else ""
    await ctx.send("", files=[self.scribus("aoitsun", message, "aoi.png")])

  @commands.command()
  async def aoisay(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "Nya."
    await ctx.send("", files=[self.scribus("aoisay", message, "aoi.png")])

  @commands.command()
  async def aoithink(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "Nya..."
    await ctx.send("", files=[self.scribus("aoithink", message, "aoi.png")])

  @commands.command()
  async def aoiwave(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "Nya!"
    await ctx.send("", files=[self.scribus("aoiwave", message, "aoi.png")])

  @commands.command()
  async def aoiexcite(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "Nya~"
    await ctx.send("", files=[self.scribus("aoiexcite", message, "aoi.png")])

  @commands.command()
  async def aoiwhisper(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "You cute!"
    await ctx.send("", files=[self.scribus("aoiwhisper", message, "aoi.png")])

  @commands.command()
  async def aoieat(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "Mico!"
    await ctx.send("", files=[self.scribus("aoieat", message, "aoi.png")])

  @commands.command()
  async def aoiheart(self, ctx, *args):
    message = " ".join(args) if len(args) > 0 else "Mico"
    await ctx.send("", files=[self.scribus("aoiheart", message, "aoi.png")])


async def setup(bot):
  await bot.add_cog(AoiCog(bot))
