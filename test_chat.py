import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import asynccontextmanager
import discord
from chat import ChatCog, DEFAULT_CTX

class TestChatCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.bot.MODEL_MAIN = "test-model"
        self.bot.discord_id = "<@123>"
        self.bot.user.name = "TestBot"
        self.bot.user.bot = True # the bot itself
        
        self.cog = ChatCog(self.bot)
        
        self.ctx = AsyncMock()
        self.ctx.reply = AsyncMock()
        self.ctx.send = AsyncMock()
        
        self.message = MagicMock()
        self.message.author = MagicMock()
        self.message.author.bot = False
        self.message.content = "<@123> hello!"
        self.message.attachments = []
        self.message.channel = MagicMock()
        self.message.channel.guild.id = 111
        self.message.channel.id = 222
        self.message.mentions = [self.bot.user]
        self.message.reply = AsyncMock()

    @patch('chat.db.load_convo')
    @patch('chat.db.save_convo')
    async def test_newchat_command(self, mock_save, mock_load):
        # mock new_convo output
        mock_convo = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "hi user"
        mock_convo.send_message = AsyncMock(return_value=mock_response)
        mock_convo.get_history = MagicMock(return_value=["fake_history"])
        mock_convo._context = "test_context"
        
        # Override new_convo method temporarily for this test
        with patch.object(self.cog, 'new_convo', return_value=mock_convo) as mock_new_convo:
            await self.cog.newchat(self.cog, self.ctx, "custom context")
            
            mock_new_convo.assert_called_once_with(self.ctx.channel, "custom context")
            mock_convo.send_message.assert_called_once_with("hi")
            mock_save.assert_called_once()
            self.ctx.reply.assert_called_once_with("hi user")

    @patch('chat.db.load_convo')
    @patch('chat.db.save_convo')
    async def test_on_message(self, mock_save, mock_load):
        # Prevent double command processing
        self.bot.get_context = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.valid = False
        self.bot.get_context.return_value = mock_ctx
        
        # Mock typing context manager
        @asynccontextmanager
        async def mock_typing():
            yield
        self.message.channel.typing = mock_typing
        
        # Mock convo retrieval and message sending
        mock_convo = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "hello from bot"
        mock_convo.send_message = AsyncMock(return_value=mock_response)
        mock_convo.get_history = MagicMock(return_value=["fake"])
        
        with patch.object(self.cog, 'get_convo', return_value=mock_convo):
            await self.cog.on_message(self.message)
            
            # verify it responded to the message
            self.message.reply.assert_called_once_with("hello from bot")

    def test_new_convo_initialization(self):
        mock_channel = MagicMock()
        mock_channel.guild.id = 999 # Some unknown guild
        
        mock_chat_session = MagicMock()
        self.bot.gemini.aio.chats.create = MagicMock(return_value=mock_chat_session)
        
        res = self.cog.new_convo(mock_channel)
        
        # Verify it used DEFAULT_CTX
        self.assertEqual(res._context, DEFAULT_CTX)
        self.bot.gemini.aio.chats.create.assert_called_once()

if __name__ == "__main__":
    unittest.main()
