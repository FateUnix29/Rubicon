from interconnections import *
import discord


@tree.command(name="embedtest", description="Embed test command.")
async def embedtest(interaction: discord.Interaction):
    # This embed should have buttons.
    embed = discord.Embed(
        title="Embed test",
        description="This embed has buttons.",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)