import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import discord
from info import InfoCog

class TestInfoCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot = AsyncMock()
        self.cog = InfoCog(self.bot)
        
        self.ctx = AsyncMock()
        self.ctx.message = MagicMock()
        
        # Setup the author mock
        self.author = MagicMock()
        self.author.__str__.return_value = "TestUser#1234"
        self.author.display_avatar.url = "http://example.com/avatar.png"
        self.ctx.message.author = self.author
        
        self.ctx.send = AsyncMock()

    async def test_avatar_no_args(self):
        # Test .avatar with no arguments (should return author's avatar)
        await self.cog.avatar(self.cog, self.ctx)
        
        self.ctx.send.assert_called_once()
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertIsInstance(embed, discord.Embed)
        self.assertEqual(embed.title, "TestUser#1234")
        self.assertEqual(embed.image.url, "http://example.com/avatar.png")

    async def test_avatar_with_mention(self):
        # Test .avatar with a user mention
        mentioned_user = MagicMock()
        mentioned_user.__str__.return_value = "MentionedUser#5678"
        mentioned_user.display_avatar.url = "http://example.com/mentioned_avatar.png"
        
        self.ctx.bot.fetch_user = AsyncMock(return_value=mentioned_user)
        
        await self.cog.avatar(self.cog, self.ctx, "<@!987654321>")
        
        self.ctx.bot.fetch_user.assert_called_once_with(987654321)
        self.ctx.send.assert_called_once()
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertEqual(embed.title, "MentionedUser#5678")
        self.assertEqual(embed.image.url, "http://example.com/mentioned_avatar.png")

    async def test_avatar_with_name_string(self):
        # Test .avatar with a string name (searches guild members)
        guild_member = MagicMock()
        guild_member.name = "TargetName"
        guild_member.nick = None
        guild_member.__str__.return_value = "TargetName#0000"
        guild_member.display_avatar.url = "http://example.com/target_avatar.png"
        
        # Mock async for loop
        async def mock_fetch_members(limit=None):
            yield guild_member
            
        self.ctx.guild.fetch_members = mock_fetch_members
        
        await self.cog.avatar(self.cog, self.ctx, "TargetName")
        
        self.ctx.send.assert_called_once()
        args, kwargs = self.ctx.send.call_args
        embed = kwargs.get("embed")
        self.assertEqual(embed.title, "TargetName#0000")
        self.assertEqual(embed.image.url, "http://example.com/target_avatar.png")

if __name__ == "__main__":
    unittest.main()
