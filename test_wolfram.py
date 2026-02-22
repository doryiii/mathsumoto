import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
import discord
from wolfram import WolframCog, format_res

class TestWolfram(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.cog = WolframCog(self.bot)
        self.ctx = AsyncMock()
        self.ctx.reply = AsyncMock()
        
        @asynccontextmanager
        async def mock_typing():
            yield
            
        self.ctx.typing = mock_typing

    def test_format_res(self):
        self.assertEqual(format_res(None), "")
        self.assertEqual(format_res("a | b | c"), "a: b: c")
        self.assertEqual(format_res("hello world"), "hello world")

    @patch('wolfram.get_wolfram')
    async def test_domath_with_answer_and_image(self, mock_get_wolfram):
        mock_get_wolfram.return_value = ("4", b"fake_image_bytes")
        
        with patch('wolfram.discord.File') as mock_file:
            mock_file_instance = MagicMock()
            mock_file.return_value = mock_file_instance
            
            await self.cog.domath(self.cog, self.ctx, "2", "+", "2")
            
            mock_get_wolfram.assert_called_once_with("2 + 2")
            self.ctx.reply.assert_called_once_with("4", file=mock_file_instance)

    @patch('wolfram.get_wolfram')
    async def test_domath_no_answer(self, mock_get_wolfram):
        mock_get_wolfram.return_value = (None, None)
        
        await self.cog.domath(self.cog, self.ctx, "gibberish")
        
        self.ctx.reply.assert_called_once_with("sorry, I have no idea (´._.`)")

    @patch('wolfram.get_wolfram')
    async def test_domath_strips_mentions(self, mock_get_wolfram):
        mock_get_wolfram.return_value = ("answer", None)
        
        await self.cog.domath(self.cog, self.ctx, "<@123456>", "hello")
        
        # Ensure the regex strips mentions correctly before calling get_wolfram
        mock_get_wolfram.assert_called_once_with(" hello")
        self.ctx.reply.assert_called_once_with("answer")

if __name__ == "__main__":
    unittest.main()
