import discord
from discord.ext import commands

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "***Patch note bot JPをご利用いただきありがとうございます。\n"
                    "パッチノートを送信するチャンネルに ```/Active Patch.N``` を実行し、通知させるテキストチャンネルの登録をしてください。\n***"
                )
                break

async def setup(bot):
    await bot.add_cog(Welcome(bot))