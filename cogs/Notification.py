import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class Notification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    notification_types = [
        app_commands.Choice(name="LoLのみ", value="lol"),
        app_commands.Choice(name="TFTのみ", value="tft"),
        app_commands.Choice(name="両方", value="both")
    ]

    @app_commands.command(name='active_patch_n', description='パッチノート通知の設定を行います。')
    @app_commands.choices(notification_type=notification_types)
    @app_commands.checks.has_permissions(administrator=True)
    async def active_patch_n(self, interaction: discord.Interaction, channel: discord.TextChannel, notification_type: str):
        guild_id = interaction.guild_id
        channel_id = channel.id

        conn = sqlite3.connect('data/notifications.db')
        c = conn.cursor()

        c.execute('SELECT id FROM notifications WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))
        existing_setting = c.fetchone()

        if existing_setting:
            c.execute('UPDATE notifications SET notification_type = ? WHERE id = ?', (notification_type, existing_setting[0]))
        else:
            c.execute('INSERT INTO notifications (guild_id, channel_id, notification_type) VALUES (?, ?, ?)',
                      (guild_id, channel_id, notification_type))

        conn.commit()
        conn.close()

        await interaction.response.send_message(f'{channel.mention} に {notification_type} の通知を設定しました。')
        

    @app_commands.command(name='deactivate_patch_n', description='パッチノート通知を無効にします。')
    @app_commands.checks.has_permissions(administrator=True)
    async def deactivate_patch_n(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
    
        conn = sqlite3.connect('data/notifications.db')
        c = conn.cursor()
    
        c.execute('DELETE FROM notifications WHERE guild_id = ?', (guild_id,))
    
        conn.commit()
        conn.close()
    
        await interaction.response.send_message('パッチノート通知が無効になりました。')

    @active_patch_n.error
    @deactivate_patch_n.error
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message('管理者以外のユーザーはこのコマンドを実行できません。', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Notification(bot))