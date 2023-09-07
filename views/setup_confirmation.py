from typing import Optional
import discord
import os
import aiomysql
from views.ticketcreation import TicketCreation

class SetupConfirmationView(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="Start the setup process", emoji="🔧")
    async def setup_confirmation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        conn = await aiomysql.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DB"),
            autocommit=True
        )
        cursor = await conn.cursor()

        ticket_channel = await interaction.guild.create_text_channel("create-ticket")
        await ticket_channel.set_permissions(interaction.guild.default_role, send_messages=False)

        message = await ticket_channel.send("✉️ Click the button to create a new ticket!", view=TicketCreation(label="Create a ticket"))

        await cursor.execute("INSERT INTO ticket_button_messages (SERVERID, MESSAGE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE MESSAGE = %s", (interaction.guild.id, "Create a ticket", "Create a ticket",))

        ticket_category = await interaction.guild.create_category("modmail-tickets")

        await cursor.execute("INSERT INTO ticket_categories (SERVERID, CATEGORYID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE CATEGORYID = %s", (interaction.guild.id, ticket_category.id, ticket_category.id,))

        await cursor.execute("INSERT INTO ticket_messages (SERVERID, CHANNELID, MESSAGEID) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE CHANNELID = %s, MESSAGEID = %s", (interaction.guild.id, ticket_channel.id, message.id, ticket_channel.id, message.id,))

        await cursor.execute("INSERT INTO ticket_channels (SERVERID, CHANNELID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE CHANNELID = %s", (interaction.guild.id, ticket_channel.id, ticket_channel.id,))

        category = await interaction.guild.create_category("modmail-logging")
        await category.set_permissions(interaction.guild.default_role, view_channel=False)
        await cursor.execute("INSERT INTO setup_category (SERVERID, CATEGORYID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE CATEGORYID = %s", (interaction.guild.id, category.id, category.id,))

        await cursor.execute("SELECT CATEGORYID FROM setup_category WHERE SERVERID = %s", (interaction.guild.id,))
        category_id = await cursor.fetchone()

        category = interaction.guild.get_channel(int(category_id[0]))
        log_channel = await interaction.guild.create_text_channel("modmail-logs", category=category)
        await log_channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await cursor.execute("INSERT INTO log_channels (SERVERID, CHANNELID) VALUES (%s, %s) ON DUPLICATE KEY UPDATE CHANNELID = %s", (interaction.guild.id, log_channel.id, log_channel.id,))

        ticket_manager_role = await interaction.guild.create_role(name="Ticket Manager", color=discord.Color.blue())
        await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, ROLEID, STATE) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE ROLEID = %s, STATE = %s", (interaction.guild.id, ticket_manager_role.id, "enabled", ticket_manager_role.id, "enabled",))
        await cursor.close()
        conn.close()
        await interaction.followup.send(f"✅ Setup done.\n\n✉️ Channel for creating tickets: {ticket_channel.mention}\n\nTicket category: **{ticket_category.name}**\n\n📝 Category for logging-related channels: **{category.name}**\n\n📝 Ticket logging channel: {log_channel.mention}\n\n🔧 Ticket Manager role: {ticket_manager_role.mention} the Ticket Manager role setting can be enabled/disabled by using `/ticketmanager` **(enabled by default)** and the role can be changed by using `/ticketmanager-role`\n\n**Please take a look at the channel settings, category settings & role settings and customise them if needed!**")