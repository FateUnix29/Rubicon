#######################################################################################################################################
##                                                                                                                                   ##
##                                                   RUBICON V4 - See _ver constant                                                  ##
##                                      'Your friendly, nuts Discord bot, and ingame companion.'                                     ##
##                                                                                                                                   ##
##                               Authored by Kite (Discord: @kitethelunatic, Github: Copper/FateUnix29)                              ##
##                                      Find Rubicon here: https://github.com/FateUnix29/Rubicon                                     ##
##                                          (Please do note: There is an older 3.x branch!)                                          ##
##                                                                                                                                   ##
##                          Licensed under the GNU GPL v3.0: https://www.gnu.org/licenses/gpl-3.0.en.html.                           ##
##                                                                                                                                   ##
##                                                                                                                                   ##
#######################################################################################################################################

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                   Imports: External Libraries                                                   ###
#-------------------------------------------------------------------------------------------------------------------------------------#

import os                                         # OS                 || Functions for interacting with the OS. Mostly used for pathing.
import sys                                        # System             || The operating system and information about it.
import signal                                     # Signal             || Functions for handling signals.
import jurigged                                   # Jurigged           || Functions for hot code reloading. Your eyes do not decieve you.
import importlib                                  # Importlib          || Importing stuff. Hot code reloading.
import importlib.util                             # Importlib          || Importing stuff. Hot code reloading.
import traceback                                  # Traceback          || Functions for debugging.

from os.path import \
    realpath, dirname, join as pjoin, exists      # Pathing            || Functions for pathing. Used much more commonly than the rest.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                      Imports: Source Files                                                      ###
#-------------------------------------------------------------------------------------------------------------------------------------#

from resources.other.colors import *              # ANSI Color Coding  || Terminal color coding.
from interconnections import *                    # Interconnections   || The interconnections between the different files.
from modules import *                             # Modules            || The modules of the bot. Still not a circular import, thus letting them start.
from resources.ai.basic import *                  # AI Basic           || The primary functions of the AI.

#######################################################################################################################################

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                       Globals & Constants                                                       ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# Almost all declared in interconnections.py.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                     Initialization (Stage 1)                                                    ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# Signal handler

def signal_handler(_, __):
    """
    Handler for SIGINT signal (Ctrl+C).
    
    Closes the log file and exits the program gracefully.
    """
    logger.error("Exiting safely: Interrupt recieved.")
    file_handler.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

logger.info(f"Hello World! Rubicon has started initialization (Stage 1).")

py_ver_dev_with = "3.12.6"                                                             # Python version to check against.

if not sys.version.startswith(py_ver_dev_with):
    FM.header_warn("Python Version", f"Your Python version ({sys.version}) does not match the development version ({py_ver_dev_with}). Please be careful.")
    logger.warning(f"We were developed with Python {py_ver_dev_with}, but we're being ran with {sys.version}. Could completely hault execution in some edge cases.")
    
logger.info(f"We have finished stage 1 initialization.")

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                            Functions                                                            ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# Almost all functions in interconnections.py.

def reload_modules():
    """A revolutionary new feature of Rubicon 4. Along with the modules system, you will be able to reload modules at any time.
    This function is to be called manually, to trigger recognition of new module files.
    
    :return: Nothing.
    :rtype: None"""

    init_file = pjoin(file_directory, 'modules', '__init__.py')
    if not exists(init_file):
        raise FileNotFoundError(f"Somehow failed to find modules init. Should be impossible. Your Rubicon installation is corrupt: {init_file}")
    
    # Non-Fancy reload - __init__.py must detect any filesystem changes, and for that, it must be entirely refreshed
    spec = importlib.util.spec_from_file_location('package', init_file)
    package = importlib.util.module_from_spec(spec)
    
    _pkgdirname = pjoin(file_directory, 'modules')
    package.__all__ = [f[:-3] for f in os.listdir(_pkgdirname) if f.endswith(".py") and not f.startswith("_")]
    
    spec.loader.exec_module(package)

    logger.info(f"Reloaded modules init, updated __all__: {package.__all__}")

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                        Discord Functions                                                        ###
#-------------------------------------------------------------------------------------------------------------------------------------#

@client.event
async def on_ready():
    print(f"{FM.info} Logged in as {client.user}::{client.user.id}...")
    for _, module in get_staged_modules(modules_readyhook, 1).items():
        if module[-1]: await module[0](locals()) # -1: Is a coro?
        else:          module[0](locals())
    logger.info("We've begun watching for updates.")
    jurigged.watch() # EVERYWHERE is now reloading.
    logger.info("Syncing...")
    #await tree.sync(guild=client.get_guild(1227389349268557894))
    await tree.sync()
    logger.info("Synced.")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user: return
    if message.content.lower().startswith("rubicon, show this man the facts"):
        print("showing this man the facts")
        await message.channel.send("<:thisthing:1279559563540172831>")


@tree.command(name="refresh_modules", description="Checks for new module source files by reloading __init__.py.")
async def refresh_modules_CMD(ctx: discord.interactions.Interaction):
    """Checks for new module source files by reloading __init__.py."""
    await ctx.response.send_message("Refreshing modules...")
    logger.info("Refreshing modules...")
    reload_modules()
    logger.info("Refreshed modules.")
    await ctx.channel.send("Refreshed modules. Syncing...")
    logger.info("Syncing...")
    await tree.sync()
    logger.info("Synced.")
    await ctx.channel.send("Synced.")
    jurigged.watch()

@tree.command(name="force_sync", description="Force Rubicon to sync it's commands with all servers.")
async def force_sync_CMD(ctx: discord.interactions.Interaction, server_id: str | None = None):
    await ctx.response.send_message("Force syncing...")
    logger.info("Force syncing...")
    if not server_id:
        await tree.sync()
        logger.info("Synced to all servers.")
        await ctx.channel.send("Synced to all servers.")
    else:
        await tree.sync(guild=discord.Object(id=server_id))
        logger.info(f"Synced to server {server_id}.")
        await ctx.channel.send(f"Synced to server {server_id}.")


client.run(discord_token)

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                             Cleanup                                                             ###
#-------------------------------------------------------------------------------------------------------------------------------------#