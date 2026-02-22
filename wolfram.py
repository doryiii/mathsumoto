import io
import re
import aiohttp
import xmltodict
import urllib.parse
import discord
from discord.ext import commands

API_URL = "http://api.wolframalpha.com/v2/query"


def format_res(txt):
    if txt is None:
        return ""
    return txt.replace(" | ", ": ")


async def get_img(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return io.BytesIO(await resp.read())


async def get_wolfram(message, app_id):
    """ Queries Wolfram Alpha. """
    url = f"{API_URL}?appid={app_id}&input={urllib.parse.quote(message)}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"failed to query WA: status {resp.status}")
                    return (None, None)
                xml_data = await resp.text()

        data = xmltodict.parse(xml_data)
        res = data.get('queryresult')
        if not res:
            return (None, None)

    except Exception as e:
        print("failed to query WA or parse response: " + str(e))
        return (None, None)

    if res.get("@success") == "true":
        pods = res.get("pod", [])
        if isinstance(pods, dict):
            pods = [pods]

        # Find primary result
        result_pod = None
        for pod in pods:
            if pod.get("@primary") == "true" or pod.get("@title") == "Result":
                result_pod = pod
                break

        if result_pod:
            subpods = result_pod.get("subpod", [])
            if isinstance(subpods, dict):
                subpods = [subpods]

            ans_parts = []
            for sub in subpods:
                pt = sub.get("plaintext")
                if pt:
                    ans_parts.append(pt)

            ans = "\n".join(ans_parts)
            result_text = format_res(ans)
            img = None

            # Special handling for number lines and plots and dice
            for pod in pods:
                pod_id = pod.get("@id")
                pod_scanner = pod.get("@scanner")

                if pod_id in ["RootPlot", "NumberLine"]:
                    subpods = pod.get("subpod", [])
                    if isinstance(subpods, dict):
                        subpods = [subpods]
                    if subpods and "img" in subpods[0]:
                        url = subpods[0]["img"].get("@src")
                        if url:
                            img = await get_img(url)
                            break

                elif pod_id == "Example" and pod_scanner == "Dice":
                    subpods = pod.get("subpod", [])
                    if isinstance(subpods, dict):
                        subpods = [subpods]
                    if subpods and "img" in subpods[0]:
                        url = subpods[0]["img"].get("@src")
                        if url:
                            img = await get_img(url)
                            break

            return (result_text, img)

        else:
            answer = None
            for pod in pods:
                pod_id = pod.get("@id")
                pod_title = pod.get("@title")

                # Plots have no "results"
                if pod_id in ["Plot", "ImplicitPlot", "3DPlot"]:
                    subpods = pod.get("subpod", [])
                    if isinstance(subpods, dict):
                        subpods = [subpods]
                    if subpods and "img" in subpods[0]:
                        url = subpods[0]["img"].get("@src")
                        if url:
                            return "Plot:", await get_img(url)

                # Other cases, look for closest answer
                elif pod_title == "Input interpretation":
                    subpods = pod.get("subpod", [])
                    if isinstance(subpods, dict):
                        subpods = [subpods]
                    if subpods:
                        text = subpods[0].get("plaintext")
                        if text:
                            answer = ("I don't know. Maybe you meant " +
                                      f"'{format_res(text)}'?")

            return answer, None

    elif "didyoumeans" in res:
        dym = res["didyoumeans"]
        items = dym.get("didyoumean", [])
        if isinstance(items, dict):
            items = [items]

        if items:
            # If multiple, find best score
            if len(items) == 1:
                best = items[0]
            else:
                best = max(items, key=lambda x: float(x.get("@score", 0)))

            if best.get("@level") != "low":
                val = best.get("#text")
                if val:
                    ans, img = await get_wolfram(val)
                    return 'I think you meant "{}": {}'.format(val, ans), img

    elif "futuretopic" in res:
        topic = res["futuretopic"].get("@topic")
        return ("I'm still learning about {} ( 〃．．)".format(topic), None)

    return (None, None)

class WolframCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def domath(self, ctx, *args):
        async with ctx.typing():
            question = " ".join(args)
            ans, img = await get_wolfram(
                re.sub(r"<@[^>]*>", "", question),
                self.bot.WOLFRAM_ALPHA_APP_ID
            )

            if not ans:
                ans = "sorry, I have no idea (´._.`)"

        if img:
            await ctx.reply(ans, file=discord.File(img, "img.gif"))
        else:
            await ctx.reply(ans)

async def setup(bot):
    await bot.add_cog(WolframCog(bot))

