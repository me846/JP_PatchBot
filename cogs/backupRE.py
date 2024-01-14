import discord
from discord.ext import commands
import os
import shutil

class ReBackupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='backupLI')
    @commands.is_owner()
    async def list_backups(self, ctx):
        backup_files = os.listdir('data/')
        backup_files = [f for f in backup_files if f.startswith('notifications.db.backup_')]
        if backup_files:
            embed = discord.Embed(
                title="利用可能なバックアップファイル",
                description="```" + "\n".join(backup_files) + "```",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("***バックアップファイルが見つかりませんでした。***")

    @commands.command(name='backupRE')
    @commands.is_owner()
    async def restore_backup(self, ctx, backup_file_name):
        backup_path = os.path.join('data/', backup_file_name)
        if os.path.exists(backup_path):
            shutil.copyfile(backup_path, 'data/notifications.db')
            await ctx.send(f"***バックアップファイル {backup_file_name} からデータベースを復旧しました。***")
        else:
            await ctx.send("***指定されたバックアップファイルが存在しません。***")

    @commands.command(name='backupDL')
    @commands.is_owner()
    async def download_backup(self, ctx, backup_file_name):
        backup_path = os.path.join('data/', backup_file_name)
        if os.path.exists(backup_path):
            await ctx.send(f"***バックアップファイル {backup_file_name} をダウンロードします。***", file=discord.File(backup_path))
        else:
            await ctx.send("***指定されたバックアップファイルが存在しません。***")

async def setup(bot):
    await bot.add_cog(ReBackupCommands(bot))
