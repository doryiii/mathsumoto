from transcription import TranscriptionCog
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import discord
import sys

# Mock voice_recv and speech_recognition BEFORE importing the cog
sys.modules['discord.ext.voice_recv'] = MagicMock()
sys.modules['discord.ext.voice_recv.extras'] = MagicMock()
sys.modules['discord.ext.voice_recv.extras.speechrecognition'] = MagicMock()


class TestTranscriptionCog(unittest.IsolatedAsyncioTestCase):
  def setUp(self):
    self.bot = AsyncMock()
    self.bot.WHISPER_KEY = "dummy_key"
    self.bot.WHISPER_URL = "http://dummy_url"

    with patch('transcription.openai.OpenAI'):
      with patch('transcription.OpenAICompatibleRecognizer'):
        self.cog = TranscriptionCog(self.bot)

    self.ctx = AsyncMock()
    self.ctx.send = AsyncMock()
    self.ctx.author.name = "TestUser"
    self.ctx.author.id = 12345
    self.ctx.author.mention = "<@12345>"
    self.ctx.channel.id = 987
    self.ctx.guild.id = 654

  async def test_transcribe_not_in_voice(self):
    self.ctx.author.voice = None

    await self.cog.transcribe(self.cog, self.ctx)

    self.ctx.send.assert_called_once_with(
      "TestUser is not in a voice channel.")

  async def test_stoptranscribe_not_in_voice(self):
    self.ctx.voice_client = None
    await self.cog.stoptranscribe(self.cog, self.ctx)

    # Verify it just returns cleanly (based on the snippet we read: `if not ctx.voice_client: return`)
    self.ctx.send.assert_not_called()

  async def test_stoptranscribe_in_voice(self):
    mock_vc = AsyncMock()
    self.ctx.voice_client = mock_vc

    await self.cog.stoptranscribe(self.cog, self.ctx)

    mock_vc.stop.assert_called_once()
    mock_vc.disconnect.assert_called_once()
    self.ctx.send.assert_called_once_with("Bye~")

  @patch('transcription.db')
  async def test_ignoreme(self, mock_db):
    self.ctx.author.id = 12345
    self.ctx.author.mention = "<@12345>"
    self.cog.ignored_users[(987, 654)] = set()
    await self.cog.ignoreme(self.cog, self.ctx)
    self.assertIn(12345, self.cog.ignored_users[(987, 654)])
    mock_db.add_ignored_user.assert_called_once_with(987, 654, 12345)
    self.ctx.send.assert_called_once_with(
      "Okay, I will ignore your voice in this channel, <@12345>.")

  @patch('transcription.db')
  async def test_unignoreme(self, mock_db):
    self.ctx.author.id = 12345
    self.ctx.author.mention = "<@12345>"
    self.cog.ignored_users[(987, 654)] = {12345}

    await self.cog.unignoreme(self.cog, self.ctx)
    self.assertNotIn(12345, self.cog.ignored_users)
    mock_db.remove_ignored_user.assert_called_once_with(987, 654, 12345)
    self.ctx.send.assert_called_once_with(
      "I will listen to your voice again in this channel, <@12345>.")

  @patch('transcription.db')
  async def test_ignoredusers(self, mock_db):
    mock_db.get_ignored_users.return_value = {123, 456}
    await self.cog.ignoredusers(self.cog, self.ctx)
    self.ctx.send.assert_called_once()
    args, kwargs = self.ctx.send.call_args
    self.assertTrue("Currently ignored users in this channel: " in args[0])
    self.assertTrue("<@123>" in args[0])
    self.assertTrue("<@456>" in args[0])

  @patch('transcription.db')
  async def test_ignoredusers_empty(self, mock_db):
    mock_db.get_ignored_users.return_value = set()
    await self.cog.ignoredusers(self.cog, self.ctx)
    self.ctx.send.assert_called_once_with(
      "No users are currently being ignored in this channel.")


if __name__ == "__main__":
  unittest.main()
