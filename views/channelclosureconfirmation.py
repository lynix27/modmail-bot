import discord
import asyncio
import aiomysql
from funcs.language_check import language_check
import json

class ChannelClosureConfirmation(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm closure", style=discord.ButtonStyle.green, custom_id="button:confirm_closure", emoji="✅")
    async def confirm_closure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True, ephemeral=True)

        lang = await language_check(interaction.guild.id)

        with open("db.json", "r") as f:
            db = json.load(f)
        conn = await aiomysql.connect(
            host=db["HOST"],
            user=db["USER"],
            password=db["PASSWORD"],
            db=db["DB"],
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute("SELECT CATEGORYID FROM ticket_categories WHERE SERVERID = %s", (interaction.guild.id,))
        result1 = await cursor.fetchone()
        if result1 is None:
            await cursor.close()
            conn.close()
            await interaction.followup.send(lang.NOT_SETUP_YET, ephemeral=True)
            return
        else:
            try:
                category = await interaction.guild.fetch_channel(result1[0])
            except:
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.SAVED_TICKET_CHANNEL_NOT_EXISTING_ANYMORE)
                return
            if interaction.channel in category.channels:
                pass
            else:
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.CHANNEL_NOT_A_TICKET_CHANNEL)
                return
        await cursor.execute("SELECT CHANNELID from log_channels WHERE SERVERID = %s", (interaction.guild.id,))
        result2 = await cursor.fetchone()
        if result2 is None:
            await cursor.close()
            conn.close()
            pass
        else:
            log_channel = interaction.guild.get_channel(int(result2[0]))
            embed = discord.Embed(title=lang.TICKET_HAS_BEEN_DELETED, description=lang.TICKET_CHANNEL_FOR_USER_DELETED_BY.format(interaction.channel.name, interaction.channel.id, interaction.user.mention, interaction.user.id))
            await cursor.close()
            conn.close()
            await log_channel.send(embed=embed)
        await interaction.followup.send(lang.CLOSING_CHANNEL_IN_FIVE_SECONDS, ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()