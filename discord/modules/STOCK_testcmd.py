from interconnections import *


@tree.command(name="testcmd", description="Test command")
async def testcmd(interaction: discord.Interaction):
    string = """this is a different string, rubicon never turned off: theres also this thing that says it reloaded called Update modules.STOCK_testcmd.testcmd @L4"""
    await interaction.response.send_message(string)
    print(string)
    logger.info(string)