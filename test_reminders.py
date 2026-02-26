import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import time
import discord
from reminders import RemindersCog


class TestRemindersCog(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    self.bot = AsyncMock()
    self.bot.get_channel = MagicMock()

    # Mock loop start/cancel methods so we don't actually run a background task in tests
    with patch('discord.ext.tasks.Loop.start'):
      with patch('discord.ext.tasks.Loop.cancel'):
        self.cog = RemindersCog(self.bot)

    self.ctx = AsyncMock()
    self.ctx.send = AsyncMock()
    self.ctx.author.mention = "<@111>"
    self.ctx.channel.id = 222

  @patch('reminders.db')
  @patch('reminders.dateparser.parse')
  @patch('reminders.time.time')
  async def test_remind_valid(self, mock_time, mock_parse, mock_db):
    mock_time.return_value = 1000.0

    mock_dt = MagicMock()
    mock_dt.timestamp.return_value = 2000.0
    mock_parse.return_value = mock_dt

    await self.cog.remind(self.cog, self.ctx, "me", "in", "5", "minutes", "to", "do", "something")

    mock_parse.assert_called_once_with("in 5 minutes")
    mock_db.add_reminder.assert_called_once_with(
      222, "<@111>", "do something", 2000.0)
    self.ctx.send.assert_called_once()
    args, kwargs = self.ctx.send.call_args
    self.assertTrue(
      "I will remind <@111> to do something at <t:2000:F>" in args[0])

  @patch('reminders.db')
  async def test_remind_invalid_format(self, mock_db):
    await self.cog.remind(self.cog, self.ctx, "some", "random", "text")

    self.ctx.send.assert_called_once_with(
      "Invalid format. Please use: `.remind <user> in <time> to <action>`")
    mock_db.add_reminder.assert_not_called()

  @patch('reminders.db')
  @patch('reminders.dateparser.parse')
  async def test_remind_invalid_time(self, mock_parse, mock_db):
    mock_parse.return_value = None

    await self.cog.remind(self.cog, self.ctx, "<@222>", "in", "unknown time", "to", "test")

    self.ctx.send.assert_called_once_with(
      "Sorry, I couldn't understand the time 'unknown time'.")
    mock_db.add_reminder.assert_not_called()

  @patch('reminders.db')
  @patch('reminders.time.time')
  async def test_check_reminders_task(self, mock_time, mock_db):
    # We test the core logic of check_reminders directly
    mock_time.return_value = 1000.0
    mock_db.get_due_reminders.return_value = [
        (1, "123", "<@456>", "do the dishes")
    ]

    mock_channel = AsyncMock()
    self.bot.get_channel.return_value = mock_channel

    # Call the inner function of the task
    await self.cog.check_reminders.coro(self.cog)

    self.bot.get_channel.assert_called_once_with(123)
    mock_channel.send.assert_called_once_with(
      "⏰ <@456>, you asked to be reminded to: do the dishes")
    mock_db.remove_reminder.assert_called_once_with(1)


if __name__ == "__main__":
  unittest.main()
