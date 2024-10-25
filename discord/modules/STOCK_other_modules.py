from interconnections import *
import time, traceback

@tree.command(name="loopsync", description="Loop sync command.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def loop_sync_CMD(ctx: discord.interactions.Interaction, times: int = 10):
    """Loop sync command."""
    await ctx.response.send_message("Loop syncing...")
    for i in range(times):
        logger.info(f"StockOtherModules::loop_sync_CMD: Loop syncing... {i+1}/{times}")
        await tree.sync()
        logger.info(f"StockOtherModules::loop_sync_CMD: Synced. {i+1}/{times}")
        time.sleep(5)

@rubicon_generichook("on_error")
def report_error(given_locals):
    error = given_locals["event"]
    print(f"{FM.error} StockOtherModules::report_error: Error logged: {error}\n{traceback.format_exc()}")
    logger.error(f"StockOtherModules::report_error: Error logged: {error}\n{traceback.format_exc()}")

rubicon_information("\nNOTICE: You are in an unfinished state.\nRubicon 4 is still in development.\nPlease make sure everyone knows about this.\n"
                    "Sincerely, (this message is provided by) A function that is part of the API for modules :heart:")