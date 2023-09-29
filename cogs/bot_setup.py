import discord
from discord.ext import commands
from discord import app_commands
import aiomysql
import os
from views.channelclosureconfirmation import ChannelClosureConfirmation
from views.setup_confirmation import SetupConfirmationView
from views.ticketcreation import TicketCreation
from funcs.language_check import language_check


class setup_channels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="setup", description="Set up the bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def modmail_setup(self, interaction: discord.Interaction):
        lang = await language_check(interaction.guild.id)
        await interaction.response.send_message(lang.START_SETUP_PROCESS, view=SetupConfirmationView(), ephemeral=True)


    @app_commands.command(name="close-ticket", description="Close the ticket channel")
    async def close_ticket(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        lang = await language_check(interaction.guild.id)

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
            await interaction.followup.send(lang.NOT_SETUP_YET, ephemeral=True)
            return
        
        else:
            if result[1] is None or result[1] == "enabled":
                role = interaction.guild.get_role(int(result[0]))
                if role in interaction.user.roles:
                    await cursor.close()
                    conn.close()
                    await interaction.followup.send(lang.ARE_YOU_SURE_TO_CLOSE_TICKET_CHANNEL, ephemeral=True, view=ChannelClosureConfirmation())
                    return
                else:
                    await cursor.close()
                    conn.close()
                    await interaction.followup.send(lang.NOT_ALLOWED_TO_DO_THIS, ephemeral=True)
                    return
            else:
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.ARE_YOU_SURE_TO_CLOSE_TICKET_CHANNEL, ephemeral=True, view=ChannelClosureConfirmation())
                return
                    

async def setup(bot: commands.Bot):
    bot.add_view(TicketCreation())
    bot.add_view(ChannelClosureConfirmation())
    await bot.add_cog(setup_channels(bot))