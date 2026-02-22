import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import discord
from aoi import AoiCog

class TestAoiCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.cog = AoiCog(self.bot)
        self.ctx = AsyncMock()
        self.ctx.send = AsyncMock()

    @patch('aoi.discord.File')
    @patch('aoi.random.choice')
    @patch('aoi.os.listdir')
    async def test_aoi(self, mock_listdir, mock_choice, mock_discord_file):
        mock_listdir.return_value = ["img1.png", "img2.jpg", "not_an_image.txt"]
        mock_choice.return_value = "img1.png"
        
        mock_file_instance = MagicMock()
        mock_discord_file.return_value = mock_file_instance
        
        await self.cog.aoi(self.cog, self.ctx)
        
        mock_listdir.assert_called_once_with("aoi")
        mock_choice.assert_called_once_with(["img1.png", "img2.jpg"])
        mock_discord_file.assert_called_once_with("aoi/img1.png", "aoi.png")
        
        self.ctx.send.assert_called_once_with("", files=[mock_file_instance])

    @patch.object(AoiCog, 'scribus')
    async def test_aoiyell(self, mock_scribus):
        mock_file = MagicMock()
        mock_scribus.return_value = mock_file
        
        await self.cog.aoiyell(self.cog, self.ctx, "hello", "world")
        
        mock_scribus.assert_called_once_with("aoiyell", "hello world", "aoi.png")
        self.ctx.send.assert_called_once_with("", files=[mock_file])

    @patch.object(AoiCog, 'scribus')
    async def test_aoisay_default(self, mock_scribus):
        mock_file = MagicMock()
        mock_scribus.return_value = mock_file
        
        # Calling with no args should use default "Nya."
        await self.cog.aoisay(self.cog, self.ctx)
        
        mock_scribus.assert_called_once_with("aoisay", "Nya.", "aoi.png")
        self.ctx.send.assert_called_once_with("", files=[mock_file])

    @patch('aoi.subprocess.run')
    @patch('aoi.os.listdir')
    @patch('aoi.discord.File')
    def test_scribus(self, mock_discord_file, mock_listdir, mock_subprocess_run):
        # We don't make this async because scribus is a synchronous function
        mock_listdir.return_value = ["template.sla", "not_template.txt"]
        mock_discord_file.return_value = "fake_discord_file"
        
        result = self.cog.scribus("test_subdir", "test message", "out.png")
        
        mock_listdir.assert_called_once_with("test_subdir")
        mock_subprocess_run.assert_called_once()
        self.assertEqual(result, "fake_discord_file")
        
        # Verify the subprocess call included the message
        args, kwargs = mock_subprocess_run.call_args
        self.assertIn("test message", args[0])

if __name__ == "__main__":
    unittest.main()
