from interconnections import *
import time, traceback

@tree.command(name="loopsync", description="Loop sync command.")
async def loop_sync_CMD(ctx: discord.interactions.Interaction, times: int = 10):
    """Loop sync command."""
    await ctx.response.send_message("Loop syncing...")
    for i in range(times):
        logger.info(f"Loop syncing... {i+1}/{times}")
        await tree.sync()
        logger.info(f"Synced. {i+1}/{times}")
        time.sleep(5)

@rubicon_generichook("on_error")
def report_error(given_locals):
    error = given_locals["event"]
    print(f"{FM.error} StockOtherModules::report_error: Error logged: {error}\n{traceback.format_exc()}")
    logger.error(f"StockOtherModules::report_error: Error logged: {error}\n{traceback.format_exc()}")
