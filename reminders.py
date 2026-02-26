import discord
from discord.ext import commands, tasks
import re
import time
import dateparser
import db


class RemindersCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.check_reminders.start()

  def cog_unload(self):
    self.check_reminders.cancel()

  @commands.command()
  async def remind(self, ctx, *args):
    command_str = " ".join(args)
    match = re.match(
        r"^(.*?)\s+(.*?)\s+to\s+(.*)$", command_str, re.IGNORECASE
    )

    if not match:
      await ctx.send("Please use `.remind <user> <time> to <action>`")
      return

    target_user = match.group(1).strip()
    time_str = match.group(2).strip()
    message_str = match.group(3).strip()

    # We handle "me" as the author
    if target_user.lower() == "me":
      target_user = ctx.author.mention

    # Parse the time using dateparser
    dt = dateparser.parse(time_str)
    if dt is None:
      await ctx.send(f"Sorry, I couldn't understand the time '{time_str}'.")
      return

    trigger_time = dt.timestamp()

    if trigger_time <= time.time():
      await ctx.send("That time is in the past!")
      return

    db.add_reminder(ctx.channel.id, target_user, message_str, trigger_time)
    await ctx.send(
        f"...I will tell {target_user} to {message_str} "
        f"around <t:{int(trigger_time)}:F>."
    )

  @tasks.loop(seconds=60.0)
  async def check_reminders(self):
    current_time = time.time()
    due_reminders = db.get_due_reminders(current_time)

    for rem_id, channel_id, target_user, message in due_reminders:
      channel = self.bot.get_channel(int(channel_id))
      if channel:
        try:
          await channel.send(f"⏰ {target_user}, {message}")
        except Exception as e:
          print(f"Failed to send reminder {rem_id}: {e}")
      db.remove_reminder(rem_id)

  @check_reminders.before_loop
  async def before_check_reminders(self):
    await self.bot.wait_until_ready()


async def setup(bot):
  await bot.add_cog(RemindersCog(bot))
