import os
import sys
import re
import feedparser
import pickle
import discord
import argparse

from discord.ext import commands
from pprint import pprint

PREFIX = ("@Matsumoto")
intents = discord.Intents.all()
bot = commands.Bot(PREFIX, case_insensitive=True, intents=intents)
msg = ""
CHANNEL = "bakkin-public"

@bot.event
async def on_ready():
    channel = [x for x in bot.get_all_channels() if x.name == CHANNEL][0]
    pprint(channel)
    await channel.send("@everyone", embed=msg)
    await bot.close()
    sys.exit(0)
    
def main():
    parser = argparse.ArgumentParser(description="Matsumoto Release Bot")
    parser.add_argument("token", help="Discord bot token")
    args = parser.parse_args()

    feed_obj = feedparser.parse("https://bakkin.moe/feed")
    updated = feed_obj.feed.updated_parsed

    if os.path.exists("last_updated.pickle"):
        with open("last_updated.pickle", "rb") as fd:
            last_updated = pickle.load(fd)

        if updated <= last_updated:
            return

    with open("last_updated.pickle", "wb") as fd:
        pickle.dump(updated, fd)

    entry = feed_obj.entries[0]
    imgs = re.search("""(?<=(src="))https?://.*(?=")""", entry.summary)
    img = imgs.group(0) if imgs else None
    print(img)

    global msg
    msg = discord.Embed(
        title=entry.title, url=entry.link,
        description=format_convert(entry.summary),
        color=discord.Color.from_rgb(65, 46, 53))
    msg.set_image(url=img)
    pprint(msg.to_dict())

    bot.run(args.token)

def format_convert(html):
    html = re.sub(r"\n", " ", html)
    html = re.sub(r"</?del>", "~~", html)
    html = re.sub(r"</?strong>", "**", html)
    html = re.sub(r"</?em>", "*", html)
    html = re.sub(r"</p>", "\n\n", html)
    html = re.sub(r"<br ?/?>", "\n", html)
    return re.sub(r"<[^>]*>", "", html).strip()

if __name__ == "__main__":
    main()

