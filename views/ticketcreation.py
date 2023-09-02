import discord
import aiomysql
import os

class TicketCreation(discord.ui.View):
    def __init__(self, label: str=None):
        super().__init__(timeout=None)
        self.label = label

        self.button1 = discord.ui.Button(label="Create a ticket", style=discord.ButtonStyle.green, custom_id="button:create_ticket", emoji="📩")
        
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