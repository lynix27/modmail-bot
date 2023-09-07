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
        await cursor.execute("SELECT CATEGORYID FROM ticket_categories WHERE SERVERID = %s", (interaction.guild.id,))
        result1 = await cursor.fetchone()
        if result1 is None:
            await cursor.close()
            conn.close()
            await interaction.followup.send("❗ I am not set up yet. Please use `/setup` to do that.", ephemeral=True)
            return
        else:
            try:
                category = await interaction.guild.fetch_channel(result1[0])
            except:
                await cursor.close()
                conn.close()
                await interaction.followup.send("❗ The saved ticket channel category doesn't exist anymore! Please define a new one by using `/ticket-category`!")
                return
            if interaction.channel in category.channels:
                pass
            else:
                await cursor.close()
                conn.close()
                await interaction.followup.send("❗ The channel you are in is not a ticket channel!")
                return
        await cursor.execute("SELECT CHANNELID from log_channels WHERE SERVERID = %s", (interaction.guild.id,))
        result2 = await cursor.fetchone()
        if result2 is None:
            await cursor.close()
            conn.close()
            pass
        else:
            log_channel = interaction.guild.get_channel(int(result2[0]))
            embed = discord.Embed(title="🗑️ Ticket has been deleted", description=f"The ticket channel for the user **{interaction.channel.name}** (**{interaction.channel.id}**) has been deleted by {interaction.user.mention} (**{interaction.user.id}**).")
            await cursor.close()
            conn.close()
            await log_channel.send(embed=embed)
        await interaction.followup.send("✅ Closing the channel in 5 seconds.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()