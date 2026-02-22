import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import discord
import sys

# Mock voice_recv and speech_recognition BEFORE importing the cog
sys.modules['discord.ext.voice_recv'] = MagicMock()
sys.modules['discord.ext.voice_recv.extras'] = MagicMock()
sys.modules['discord.ext.voice_recv.extras.speechrecognition'] = MagicMock()

from transcription import TranscriptionCog

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

    async def test_transcribe_not_in_voice(self):
        self.ctx.author.voice = None
        
        await self.cog.transcribe(self.cog, self.ctx)
        
        self.ctx.send.assert_called_once_with("TestUser is not in a voice channel.")

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

if __name__ == "__main__":
    unittest.main()
