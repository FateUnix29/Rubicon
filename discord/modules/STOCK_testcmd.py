from interconnections import *


@tree.command(name="testcmd", description="Test command")
async def testcmd(interaction: discord.Interaction):
    string = """```py
@tree.command(name="testcmd", description="Test command")
async def testcmd(interaction: discord.Interaction):
    string = "Rubicon is alive! Good to go!"
    await interaction.response.send_message(string)
    print(string)
    logger.info(string)
```"""
    await interaction.response.send_message(string)
    print(string)
    logger.info(string)