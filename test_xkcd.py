import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import discord
from xkcd import XkcdCog

from contextlib import asynccontextmanager

class TestXkcdCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.cog = XkcdCog(self.bot)
        self.ctx = AsyncMock()
        self.ctx.reply = AsyncMock()
        
        @asynccontextmanager
        async def mock_typing():
            yield
            
        self.ctx.typing = mock_typing

    @patch('xkcd.requests.post')
    async def test_xkcd_with_alternates(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "123", "title": "Main Comic", "alt": "Main Alt", "img": "http://example.com/123.jpg", "score": 0.9},
            {"id": "456", "title": "Alt Comic 1", "score": 0.5},
            {"id": "789", "title": "Alt Comic 2", "score": 0.3} # Should be filtered out due to score < 0.4
        ]
        mock_post.return_value = mock_response

        await self.cog.xkcd(self.cog, self.ctx, "test", "query")

        mock_post.assert_called_once_with("http://localhost:9523", "test query")
        self.ctx.reply.assert_called_once()
        
        args, kwargs = self.ctx.reply.call_args
        embed = kwargs.get("embed")
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.title, "Main Comic")
        self.assertEqual(embed.url, "https://xkcd.com/123")
        self.assertEqual(embed.description, "Main Alt")
        self.assertEqual(embed.image.url, "http://example.com/123.jpg")
        
        # Verify alternates logic - 789 should be omitted
        expected_footer = "cosine: 0.9000\n\nSee also:\nhttps://xkcd.com/456 Alt Comic 1 (0.5000)"
        self.assertEqual(embed.footer.text, expected_footer)

    @patch('xkcd.requests.post')
    async def test_xkcd_no_alternates(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": "123", "title": "Single Comic", "img": "http://example.com/123.jpg"} # No alt text, no score
        ]
        mock_post.return_value = mock_response

        await self.cog.xkcd(self.cog, self.ctx, "test", "query")

        self.ctx.reply.assert_called_once()
        args, kwargs = self.ctx.reply.call_args
        embed = kwargs.get("embed")
        self.assertEqual(embed.title, "Single Comic")
        self.assertEqual(embed.description, "") # defaults to ""
        self.assertEqual(embed.footer.text, "cosine: ")

if __name__ == "__main__":
    unittest.main()
