import discord
import aiomysql
from funcs.language_check import language_check
import json

class TicketCreation(discord.ui.View):
    def __init__(self, label: str=None, message: str=None):
        super().__init__(timeout=None)
        self.label = label
        self.message = message

        if self.label == "":
            self.button1 = discord.ui.Button(label=self.message, style=discord.ButtonStyle.green, custom_id="button:create_ticket", emoji="📩")
        else:
            self.button1 = discord.ui.Button(label=str(self.label), style=discord.ButtonStyle.green, custom_id="button:create_ticket", emoji="📩")
        
        async def button1_callback(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True, thinking=True)

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
            category_id = await cursor.fetchone()

            overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)}
            category = interaction.guild.get_channel(int(category_id[0]))

            if discord.utils.get(category.text_channels, name=f"{interaction.user.name}"):
                await cursor.close()
                conn.close()
                await interaction.followup.send(lang.ALREADY_OPEN_TICKET_CHANNEL, ephemeral=True)
                return


            channel = await category.create_text_channel(name=interaction.user.name, overwrites=overwrites)

            await cursor.execute("SELECT CHANNELID from log_channels WHERE SERVERID = %s", (interaction.guild.id,))
            result = await cursor.fetchone()
            if result is None:
                pass
            else:
                try:
                    log_channel = interaction.guild.get_channel(int(result[0]))
                    embed = discord.Embed(title=lang.TICKET_HAS_BEEN_CREATED, description=lang.TICKET_CHANNEL_FOR_USER_CREATED_BY.format(channel.name, channel.id, interaction.user.mention, interaction.user.id))
                    await log_channel.send(embed=embed)
                except:
                    pass

            await cursor.close()
            conn.close()
            await interaction.followup.send(lang.TICKET_CHANNEL_CREATED.format(channel.mention), ephemeral=True)



        self.button1.callback = button1_callback

        self.add_item(self.button1)