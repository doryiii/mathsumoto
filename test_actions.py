import unittest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
import discord
from actions import ActionsCog

class TestActionsCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.bot.user.name = "TestBot"
        self.cog = ActionsCog(self.bot)
        self.ctx = AsyncMock()
        self.ctx.send = AsyncMock()
        self.ctx.reply = AsyncMock()
        self.ctx.author.display_name = "UserA"
        self.ctx.message.author.name = "UserA"

    async def test_bot_send(self):
        await self.cog.bot_send(self.ctx, "Hello!")
        self.ctx.send.assert_called_once()
        args, kwargs = self.ctx.send.call_args
        self.assertEqual(kwargs['embed'].description, "Hello!")

    @patch('actions.re.findall')
    async def test_get_user_from_mention(self, mock_findall):
        mock_findall.return_value = ["1234"]
        
        # Test guild member fetch
        mock_member = MagicMock()
        mock_member.display_name = "GuildUser"
        self.ctx.guild.fetch_member = AsyncMock(return_value=mock_member)
        
        name = await self.cog.get_user_from_mention(self.ctx, "<@1234>")
        self.assertEqual(name, "GuildUser")
        
        # Test non-mention fallback
        mock_findall.return_value = []
        name = await self.cog.get_user_from_mention(self.ctx, "PlainName")
        self.assertEqual(name, "PlainName")

    @patch('actions.random.choice')
    @patch('builtins.open', new_callable=mock_open, read_data="{orig} hugged {dest}\\n")
    @patch.object(ActionsCog, 'bot_send')
    async def test_hug_no_args(self, mock_bot_send, mock_file, mock_choice):
        mock_choice.side_effect = [False, "{orig} hugged {dest}"] # False for use_ai
        
        await self.cog.hug(self.cog, self.ctx)
        
        mock_bot_send.assert_called_once_with(self.ctx, "**TestBot** hugged **UserA**")

    @patch('actions.random.choice')
    @patch('builtins.open', new_callable=mock_open, read_data="{orig} kissed {dest}\\n")
    @patch.object(ActionsCog, 'bot_send')
    async def test_kiss_one_arg(self, mock_bot_send, mock_file, mock_choice):
        mock_choice.return_value = "{orig} kissed {dest}"
        
        # Mock get_user_from_mention so it just returns what we pass it
        with patch.object(ActionsCog, 'get_user_from_mention', return_value="UserB"):
            await self.cog.kiss(self.cog, self.ctx, "UserB")
            
        mock_bot_send.assert_called_once_with(self.ctx, "**UserA** kissed **UserB**")

    @patch('actions.random.randint')
    async def test_askrise(self, mock_randint):
        mock_randint.return_value = 5
        await self.cog.askrise(self.cog, self.ctx)
        
        self.ctx.reply.assert_called_once()
        args, kwargs = self.ctx.reply.call_args
        self.assertEqual(kwargs['embed'].description, ".....")

if __name__ == "__main__":
    unittest.main()
