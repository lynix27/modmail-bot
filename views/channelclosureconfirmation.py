import discord
import asyncio
import aiomysql
import os

class ChannelClosureConfirmation(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm closure", style=discord.ButtonStyle.green, custom_id="button:confirm_closure", emoji="✅")
    async def confirm_closure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True, ephemeral=True)
        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute("SELECT CHANNELID from log_channels WHERE SERVERID = %s", (interaction.guild.id,))
        result = await cursor.fetchone()
        if result is None:
            await cursor.close()
            conn.close()
            pass
        else:
            log_channel = interaction.guild.get_channel(int(result[0]))
            embed = discord.Embed(title="🗑️ Channel has been deleted", description=f"The ticket channel for the user **{interaction.channel.name}** (**{interaction.channel.id}**) has been deleted by {interaction.user.mention}.")
            await cursor.close()
            conn.close()
            await log_channel.send(embed=embed)
        await interaction.followup.send("✅ Closing the channel in 5 seconds.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()