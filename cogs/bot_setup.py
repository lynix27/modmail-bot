import discord
from discord.ext import commands
from discord import app_commands
import aiomysql
import os
from views.channelclosureconfirmation import ChannelClosureConfirmation
from views.setup_confirmation import SetupConfirmationView
from views.ticketcreation import TicketCreation

class setup_channels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="setup", description="Set up the bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def modmail_setup(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔧 Do you want to start the setup process?", view=SetupConfirmationView(), ephemeral=True)


    @app_commands.command(name="close-ticket", description="Close the ticket channel")
    async def close_ticket(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute("SELECT ROLEID, STATE FROM ticket_manager_roles WHERE SERVERID = %s", (interaction.guild.id,))
        result = await cursor.fetchone()
        if result[0] is None:
            await cursor.close()
            conn.close()
            await interaction.followup.send("❗ I am not set up yet. Please use `/setup` to do that.", ephemeral=True)
            return
        
        else:
            if result[1] is None or result[1] == "enabled":
                role = interaction.guild.get_role(int(result[0]))
                if role in interaction.user.roles:
                    await cursor.close()
                    conn.close()
                    await interaction.followup.send("❗ Are you sure you want to close the ticket channel?", ephemeral=True, view=ChannelClosureConfirmation())
                    return
                else:
                    await cursor.close()
                    conn.close()
                    await interaction.followup.send("❗ You are not allowed to do this!", ephemeral=True)
                    return
            else:
                await cursor.close()
                conn.close()
                await interaction.followup.send("❗ Are you sure you want to close the ticket channel?", ephemeral=True, view=ChannelClosureConfirmation())
                return
                    

async def setup(bot: commands.Bot):
    bot.add_view(TicketCreation())
    bot.add_view(ChannelClosureConfirmation())
    await bot.add_cog(setup_channels(bot))