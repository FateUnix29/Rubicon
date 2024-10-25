from interconnections import *


@tree.command(name="ping", description="Test command")
async def testcmd(interaction: discord.Interaction):
    string = """Pong!"""
    await interaction.response.send_message(string)
    print(string)
    logger.info(string)