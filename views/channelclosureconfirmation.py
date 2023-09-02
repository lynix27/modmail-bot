import discord
import asyncio

class ChannelClosureConfirmation(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm closure", style=discord.ButtonStyle.green, custom_id="button:confirm_closure", emoji="✅")
    async def confirm_closure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Closing the channel in 5 seconds.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()