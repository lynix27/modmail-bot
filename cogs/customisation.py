import discord
from discord.ext import commands
from discord import app_commands
import os
import aiomysql
import asyncio
from views.ticketcreation import TicketCreation
from funcs.language_check import language_check

class MessageModal(discord.ui.Modal, title="Change ticket creation button message"):
    text = discord.ui.TextInput(label="Enter the new message", placeholder="Input text", min_length=1, max_length=500, style=discord.TextStyle.long)
    label = discord.ui.TextInput(label="Change the label (optional)", placeholder="Input text", min_length=1, max_length=20, style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        lang = await language_check(interaction.guild.id)

        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()

        await cursor.execute("SELECT MESSAGEID FROM ticket_messages WHERE SERVERID = %s", (interaction.guild.id,))
        messageid = await cursor.fetchone()
        if messageid is None:
            await interaction.followup.send(content=lang.NOT_SETUP_YET, ephemeral=True)
            await cursor.close()
            conn.close()
            return
        
        else:
            await cursor.execute("SELECT CHANNELID FROM ticket_messages WHERE SERVERID = %s", (interaction.guild.id,))
            channelid = await cursor.fetchone()
            if channelid is None:
                await interaction.followup.send(content=lang.NOT_SETUP_YET, ephemeral=True)
                await cursor.close()
                conn.close()
                return
            else:
                try:
                    old_message = await interaction.guild.get_channel(int(channelid[0])).fetch_message(int(messageid[0]))
                except:
                    await cursor.close()
                    conn.close()
                    await interaction.followup.send(lang.AN_ERROR_OCCURED_PLEASE_CHECK_IF_THE_MESSAGE_AND_CHANNEL_EXIST, ephemeral=True)
                    return

                if self.label.value == "":
                    await cursor.execute("SELECT MESSAGE FROM ticket_button_messages WHERE SERVERID = %s", (interaction.guild.id,))
                    res = await cursor.fetchone()
                    await old_message.edit(content=str(self.text.value), view=TicketCreation(label=str(self.label.value), message=str(res[0])))
                else:
                    await cursor.execute("INSERT INTO ticket_button_messages (SERVERID, MESSAGE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE MESSAGE = %s", (interaction.guild.id, str(self.label.value), str(self.label.value)))
                    await old_message.edit(content=str(self.text.value), view=TicketCreation(label=str(self.label.value)))
                await cursor.close()
                conn.close()

                await interaction.followup.send(content="✅ Message edited!", ephemeral=True)

class customisation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="edit-ticket-message", description="Change message and button text")
    @app_commands.checks.has_permissions(administrator=True)
    async def edit_ticket_msg(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MessageModal())

    @app_commands.command(name="ticketmanager", description="Enable or disable Ticket Manager role setting")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="enable", value=1),
            app_commands.Choice(name="disable", value=2)
        ]
    )
    async def ticketmanager(self, interaction: discord.Interaction, choice: app_commands.Choice[int]):
        await interaction.response.defer(ephemeral=True, thinking=True)

        lang = await language_check(interaction.guild.id)

        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute("SELECT ROLEID FROM ticket_manager_roles WHERE SERVERID = %s", (interaction.guild.id,))
        result = await cursor.fetchone()
        if result is None:
            await cursor.close()
            conn.close()
            await interaction.followup.send(lang.NOT_SETUP_YET, ephemeral=True)
            return
        else:
            if choice.value == 1:
                await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, STATE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE STATE = %s", (interaction.guild.id, "enabled", "enabled",))
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.TICKET_MANAGER_ROLE_NOW_ENABLED, ephemeral=True)

            if choice.value == 2:
                await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, STATE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE STATE = %s", (interaction.guild.id, "disabled", "disabled",))
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.TICKET_MANAGER_ROLE_NOW_DISABLED, ephemeral=True)


    @app_commands.command(name="ticketmanager-role", description="Change the Ticket Manager role")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketmanager_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True, thinking=True)

        lang = await language_check(interaction.guild.id)

        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute("SELECT ROLEID FROM ticket_manager_roles WHERE SERVERID = %s", (interaction.guild.id,))
        result = await cursor.fetchone()
        if result is None:
            await cursor.close()
            conn.close()
            await interaction.followup.send(lang.NOT_SETUP_YET, ephemeral=True)
            return
        else:
            await cursor.execute("SELECT STATE FROM ticket_manager_roles WHERE SERVERID = %s", (interaction.guild.id,))
            state_res = await cursor.fetchone()
            if state_res is None or state_res[0] == "enabled":
                await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, ROLEID, STATE) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE ROLEID = %s, STATE = %s", (interaction.guild.id, role.id, "enabled", role.id, "enabled",))
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.CHANGED_TICKET_MANAGER_ROLE_TO.format(role.mention), ephemeral=True)
            else:
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.TICKET_MANAGER_MODULE_DISABLED, ephemeral=True)
    
    @app_commands.command(name="ticket-category", description="Set a ticket category")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        lang = await language_check(interaction.guild.id)

        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO ticket_categories (SERVERID, CATEGORYID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE CATEGORYID = %s", (interaction.guild.id, category.id, category.id))
        await cursor.close()
        conn.close()
        await interaction.response.send_message(lang.TICKET_CHANNEL_CATEGORY_NOW_SET_TO.format(category.name), ephemeral=True)

async def setup(bot: commands.Bot):
    bot.add_view(TicketCreation())
    await bot.add_cog(customisation(bot))