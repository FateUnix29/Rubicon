from interconnections import *
from discord.ext import tasks
from random import choice
import traceback
import time, datetime

this_module_init_time = time.time()

default_stats = [
    "Running on {{version}}...",
    "The goofiest goober ever.",
    "explosion sfx",
    "Certified idiot",
    "Hehehah...........",
    "Somehow failed to find modules init. Should be impossible. Your Rubicon installation is corrupt: :trollface:",
    "Somehow online for {{uptime}} so far..."
]

def read_stats_file():
    try:
        with open(pjoin(file_directory, "status.json"), "r") as file:
            loaded = json.load(file)

            for msg in loaded:
                if not isinstance(msg, str):
                    raise TypeError("Invalid type in status.json.")

                msg = msg.replace("{version}", version)
        
        logger.info(f"StockStatus::read_stats_file || Loaded {len(loaded)} statuses... ({"'" + "', '".join(loaded) + "'"})")
        return loaded

    except FileNotFoundError:
        logger.error("StockStatus::read_stats_file || Unable to find status.json.")

        try:
            with open(pjoin(file_directory, "status.json"), "w") as file:
                json.dump(default_stats, file, indent=4)
            logger.info("StockStatus::read_stats_file || Created new status.json.")

        except Exception as e:
            logger.error(f"StockStatus::read_stats_file || Unable to write to status.json. {type(e).__name__}: {e}\n{traceback.format_exc()}")
        
        return default_stats

    except Exception as e:
        logger.error(f"StockStatus::read_stats_file || Unable to read status.json. {type(e).__name__}: {e}\n{traceback.format_exc()}")
        return default_stats
    
def write_stats_file():
    try:
        with open(pjoin(file_directory, "status.json"), "w") as file:
            json.dump(stats, file, indent=4)
        logger.info("StockStatus::write_stats_file || Wrote status.json.")
    except Exception as e:
        logger.error(f"StockStatus::write_stats_file || Unable to write to status.json. {type(e).__name__}: {e}\n{traceback.format_exc()}")

stats = read_stats_file()

@tasks.loop(seconds=10)
async def cycle_through_status():
    msgchoice = choice(stats)
    
    if "{uptime}" in msgchoice:
        msgchoice = msgchoice.replace("{uptime}", f"{datetime.timedelta(seconds=int(time.time() - this_module_init_time))}")
    if "{version}" in msgchoice:
        msgchoice = msgchoice.replace("{version}", version)

    await client.change_presence(status=discord.Status.online, activity=discord.CustomActivity(name=msgchoice))

@rubicon_readyhook(3)
def start_the_thing(_):
    cycle_through_status.start()

@tree.command(name="refresh_stats", description="Reload status.json.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def reload_status_CMD(ctx: discord.Interaction):
    global stats
    stats = read_stats_file()
    logger.info("StockStatus::reload_status_CMD || Reloaded status.json.")
    await ctx.response.send_message("Reloaded status.json.")

@tree.command(name="add_status", description="Add a status to the status.json.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def add_status_CMD(ctx: discord.Interaction, msg: str):
    global stats
    stats.append(msg)
    write_stats_file()
    logger.info(f"StockStatus::add_status_CMD || Added '{msg}' to status.json.")
    await ctx.response.send_message(f"Added `{msg}` to status.json.")