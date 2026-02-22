import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import discord
from images import ImagesCog

class TestImagesCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.cog = ImagesCog(self.bot)
        self.ctx = AsyncMock()
        self.ctx.send = AsyncMock()

    @patch('images.nekos.img')
    async def test_neko(self, mock_nekos_img):
        mock_nekos_img.return_value = "http://example.com/neko.jpg"
        
        await self.cog.neko(self.cog, self.ctx)
        
        mock_nekos_img.assert_called_once_with("neko")
        self.ctx.send.assert_called_once()
        
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.image.url, "http://example.com/neko.jpg")

    @patch('images.httpx.AsyncClient')
    async def test_inu(self, mock_async_client):
        # Setup mock for httpx response
        mock_response = MagicMock()
        mock_response.json.return_value = {"file_url": "http://example.com/inu.jpg"}
        
        # Setup context manager for AsyncClient
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        await self.cog.inu(self.cog, self.ctx)
        
        mock_client_instance.get.assert_called_once()
        self.ctx.send.assert_called_once()
        
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.image.url, "http://example.com/inu.jpg")

    @patch('images.httpx.AsyncClient')
    async def test_usagi(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"file_url": "http://example.com/usagi.jpg"}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        await self.cog.usagi(self.cog, self.ctx)
        
        mock_client_instance.get.assert_called_once()
        self.ctx.send.assert_called_once()
        
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.image.url, "http://example.com/usagi.jpg")

    @patch('images.httpx.AsyncClient')
    async def test_catboy(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"file_url": "http://example.com/catboy.jpg"}
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        await self.cog.catboy(self.cog, self.ctx)
        
        mock_client_instance.get.assert_called_once()
        self.ctx.send.assert_called_once()
        
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.image.url, "http://example.com/catboy.jpg")

if __name__ == "__main__":
    unittest.main()
