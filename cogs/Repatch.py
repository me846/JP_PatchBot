import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class RePatchCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="re_patch", description="最近のパッチノートを再投稿します。")
    @app_commands.describe(game_type="LoLかTFTかを選択してください。")
    @app_commands.choices(game_type=[
        app_commands.Choice(name="LoL", value="lol"),
        app_commands.Choice(name="TFT", value="tft"),
        app_commands.Choice(name="両方", value="both")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def re_patch(self, interaction: discord.Interaction, game_type: str):
        conn = sqlite3.connect('data/notifications.db')
        c = conn.cursor()

        if game_type != "both":
            c.execute('SELECT * FROM recent_patch_notes WHERE game_type = ?', (game_type,))
        else:
            c.execute('SELECT * FROM recent_patch_notes')
        
        patch_notes = c.fetchall()

        await interaction.response.send_message("***最近のパッチノートを再投稿します。***")
        
        for note in patch_notes:
            _, _, title, content, image_url = note
            embed = discord.Embed(title=title, description=content, color=0x0000ff)
            if image_url:
                embed.set_image(url=image_url)
            await interaction.followup.send(embed=embed)

        conn.close()

async def setup(bot):
    await bot.add_cog(RePatchCommands(bot))