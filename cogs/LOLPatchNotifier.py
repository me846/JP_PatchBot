import discord
from discord.ext import commands
import sqlite3
import requests
from bs4 import BeautifulSoup

def scrape_patch_notes(patch_number):
    formatted_patch_number = patch_number.replace('.', '-')
    url = f"https://www.leagueoflegends.com/ja-jp/news/game-updates/patch-{formatted_patch_number}-notes/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1', class_='style__Title-sc-vd48si-5').text
    content = soup.find('blockquote', class_='blockquote context').text
    highlights_image_section = soup.find("a", class_="skins cboxElement")
    highlights_image_url = highlights_image_section["href"] if highlights_image_section else None
    return title, content, highlights_image_url

class LOLPatchNotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='LPatchUP')
    @commands.is_owner()
    async def lpatch_up(self, ctx, patch_number: str = None):
        if not patch_number:
            await ctx.send('パッチナンバーを指定してください。')
            return
    
        title, content, highlights_image_url = scrape_patch_notes(patch_number)
    
        conn = sqlite3.connect('data/notifications.db')
        c = conn.cursor()
    
        c.execute('SELECT guild_id, channel_id, notification_type FROM notifications WHERE notification_type IN ("lol", "both")')
        notifications = c.fetchall()
    
        for guild_id, channel_id, _ in notifications:
            guild = self.bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(title=title, description=content, color=0x0000ff)
                    if highlights_image_url:
                        embed.set_image(url=highlights_image_url)
                    await channel.send(embed=embed)
                    
        c.execute('''
            INSERT OR REPLACE INTO recent_patch_notes (game_type, patch_number, title, content, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', ('tft', patch_number, title, content, highlights_image_url))
    
        conn.commit()
        conn.close()

    @commands.command(name='LTestUP')
    @commands.is_owner()
    async def ltest_up(self, ctx, patch_number: str = None):
        if not patch_number:
            await ctx.send('パッチナンバーを指定してください。')
            return
        
        title, content, highlights_image_url = scrape_patch_notes(patch_number)

        formatted_content = content.replace('。', '。\n').replace('!', '!\n')
        first_sentence_end = formatted_content.find('\n')
        if first_sentence_end != -1:
            formatted_content = f"**{formatted_content[:first_sentence_end + 1]}**" + formatted_content[first_sentence_end + 1:]

        embed = discord.Embed(title=title, description=formatted_content, color=0x0000ff)
        if highlights_image_url:
            embed.set_image(url=highlights_image_url)
    
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(LOLPatchNotes(bot))