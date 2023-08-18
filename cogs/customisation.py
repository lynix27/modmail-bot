import discord
from discord.ext import commands
from discord import app_commands
import os
import aiomysql
import asyncio

class TicketCreation(discord.ui.View):
    def __init__(self, label: str=None, message: str=None):
        super().__init__(timeout=None)
        self.label = label
        self.message = message

        if self.label == "":
            print("in class: label value none")
            self.button1 = discord.ui.Button(label=self.message, style=discord.ButtonStyle.green, custom_id="button:create_ticket", emoji="📩")
            print("in class: set button label to message value")
        else:
            print("in class: label value not none")
            self.button1 = discord.ui.Button(label=str(self.label), style=discord.ButtonStyle.green, custom_id="button:create_ticket", emoji="📩")
            print("in class: set button label to given value")

        async def button1_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True, thinking=True)
            conn = await aiomysql.connect(
                host=os.getenv("HOST"),
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                db=os.getenv("DB"),
                autocommit=True
            )
            cursor = await conn.cursor()
            await cursor.execute("SELECT CATEGORYID FROM ticket_categories WHERE SERVERID = %s", (interaction.guild.id,))
            category_id = await cursor.fetchone()

            overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)}
            category = interaction.guild.get_channel(int(category_id[0]))

            if discord.utils.get(category.text_channels, name=f"{interaction.user.name}"):
                await cursor.close()
                conn.close()
                await interaction.followup.send("❗ There already is an open ticket channel! Please wait for it to be closed in order to open a new one.", ephemeral=True)
                return

            channel = await category.create_text_channel(name=interaction.user.name, overwrites=overwrites)

            await cursor.close()
            conn.close()
            await interaction.followup.send(f"✅ Ticket channel created: {channel.mention}", ephemeral=True)

        self.button1.callback = button1_callback

        self.add_item(self.button1)

class MessageModal(discord.ui.Modal, title="Change ticket creation button message"):
    text = discord.ui.TextInput(label="Enter the new message", placeholder="Input text", min_length=1, max_length=500, style=discord.TextStyle.long)
    label = discord.ui.TextInput(label="Change the label (optional)", placeholder="Input text", min_length=1, max_length=20, style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
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
            await interaction.followup.send(content="❗ I am not set up yet. Please use `/setup` to do that.", ephemeral=True)
            await cursor.close()
            conn.close()
            return
        
        else:
            await cursor.execute("SELECT CHANNELID FROM ticket_messages WHERE SERVERID = %s", (interaction.guild.id,))
            channelid = await cursor.fetchone()
            if channelid is None:
                await interaction.followup.send(content="❗ I am not set up yet. Please use `/setup` to do that.", ephemeral=True)
                await cursor.close()
                conn.close()
                return
            else:
                try:
                    old_message = await interaction.guild.get_channel(int(channelid[0])).fetch_message(int(messageid[0]))
                except:
                    await cursor.close()
                    conn.close()
                    await interaction.followup.send("❗ An error occured. Please check if the message and the channel still exists. Use `/setup` to set me up again.", ephemeral=True)
                    return

                if self.label.value == "":
                    print("label value none")
                    await cursor.execute("SELECT MESSAGE FROM ticket_button_messages WHERE SERVERID = %s", (interaction.guild.id,))
                    res = await cursor.fetchone()
                    print("message fetched")
                    await old_message.edit(content=str(self.text.value), view=TicketCreation(label=str(self.label.value), message=str(res[0])))
                    print("message edited")
                else:
                    print("label value not none")
                    await cursor.execute("INSERT INTO ticket_button_messages (SERVERID, MESSAGE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE MESSAGE = %s", (interaction.guild.id, str(self.label.value), str(self.label.value)))
                    print("message saved to database")
                    await old_message.edit(content=str(self.text.value), view=TicketCreation(label=str(self.label.value)))
                    print("message edited")
                await cursor.close()
                conn.close()

                await interaction.followup.send(content="✅ Message edited!", ephemeral=True)

class customisation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="edit-ticket-message", description="Change message and button text")
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
            await interaction.followup.send("❗ I am not set up yet. Please use `/setup` to do that.", ephemeral=True)
            return
        else:
            if choice.value == 1:
                await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, STATE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE STATE = %s", (interaction.guild.id, "enabled", "enabled",))
                await cursor.close()
                conn.close()
                await interaction.followup.send("✅ Ticket Manager role is now enabled.", ephemeral=True)

            if choice.value == 2:
                await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, STATE) VALUES (%s, %s) ON DUPLICATE KEY UPDATE STATE = %s", (interaction.guild.id, "disabled", "disabled",))
                await cursor.close()
                conn.close()
                await interaction.followup.send("✅ Ticket Manager role is now disabled.", ephemeral=True)


    @app_commands.command(name="ticketmanager-role", description="Change the Ticket Manager role")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketmanager_role(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(ephemeral=True, thinking=True)
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
            await interaction.followup.send("❗ I am not set up yet. Please use `/setup` to do that.", ephemeral=True)
            return
        else:
            await cursor.execute("SELECT STATE FROM ticket_manager_roles WHERE SERVERID = %s", (interaction.guild.id,))
            state_res = await cursor.fetchone()
            if state_res is None or state_res[0] == "enabled":
                await cursor.execute("INSERT INTO ticket_manager_roles (SERVERID, ROLEID, STATE) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE ROLEID = %s, STATE = %s", (interaction.guild.id, role.id, "enabled", role.id, "enabled",))

            


async def setup(bot: commands.Bot):
    bot.add_view(TicketCreation())
    await bot.add_cog(customisation(bot))