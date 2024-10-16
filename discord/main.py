#######################################################################################################################################
##                                                                                                                                   ##
##                                                   RUBICON V4 - See config for ver                                                 ##
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

from copy import deepcopy                         # Deepcopy           || Deep copy ensures that an entirely new object is created when cloning.

from os.path import \
    realpath, dirname, join as pjoin, exists      # Pathing            || Functions for pathing. Used much more commonly than the rest.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                      Imports: Source Files                                                      ###
#-------------------------------------------------------------------------------------------------------------------------------------#

from resources.other.colors import *              # ANSI Color Coding  || Terminal color coding.
from interconnections import *                    # Interconnections   || The interconnections between the different files.
from modules import *                             # Modules            || The modules of the bot. Still not a circular import, thus letting them start.
from resources.ai.basic import *                  # AI Basic           || The primary functions of the AI.
from resources.other.datedata import *            # Date Data          || Timestamps and time information.
from resources.other.assembler import *           # Assembler          || Assembles messages into Rubicon format.

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
    for _, handler in current_loggers:
        handler.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

logger.info(f"Hello World! Rubicon has started initialization (Stage 1).")

py_ver_dev_with = "3.12.6"                                                             # Python version to check against.

if not sys.version.startswith(py_ver_dev_with):
    FM.header_warn("Python Version", f"Your Python version ({sys.version}) does not match the development version ({py_ver_dev_with}). Please be careful.")
    logger.warning(f"We were developed with Python {py_ver_dev_with}, but we're being ran with {sys.version}. Could completely hault execution in some edge cases.")
    
init_groq(groq_api_key)

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
    returned_locals = locals()
    should_return = False
    
    print(f"{FM.info} Logged in as {client.user}::{client.user.id}...")

    for module in list(get_staged_modules(modules_readyhook, 1).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        if should_return: return


    jurigged.watch() # EVERYWHERE is now reloading.
    logger.info("We've begun watching for updates.")
    logger.info("Syncing...")
    await tree.sync()
    logger.info("Synced.")


    for module in list(get_staged_modules(modules_readyhook, 2).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        if should_return: return


    # Put stage 2 code here, I suppose.


    for module in list(get_staged_modules(modules_readyhook, 3).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        if should_return: return

@client.event
async def on_message(message: discord.Message):
    global conversation # Why doesn't it register unless I do this? Come on, Python.

    message_contents = message.content # These are the essential variables that are checked for in the .get() calls for modules.
    proto_content = assemble_user_message(message, "") # This is so that message modules can utilize this to cut out the header info and modify the actual content.
    # Modify message contents with a format.
    message_contents = f"{proto_content}{message_contents}"
    
    message_has_special_character = False
    skip_general_check = False
    in_all_channel = False
    returned_locals = locals()
    
    should_return = False

    for module in list(get_staged_modules(modules_msghook, 1).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        message_contents = returned_locals.get('message_contents', message_contents)
        message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
        in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
        skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
        if should_return: return


    for module in list(get_staged_modules(modules_msghook, 2).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        message_contents = returned_locals.get('message_contents', message_contents)
        message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
        in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
        skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
        if should_return: return


    for module in list(get_staged_modules(modules_msghook, 3).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        message_contents = returned_locals.get('message_contents', message_contents)
        message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
        in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
        skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
        if should_return: return


    for module in list(get_staged_modules(modules_msghook, 4).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        message_contents = returned_locals.get('message_contents', message_contents)
        message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
        in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
        skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
        if should_return: return

    print(f"{FM.light_blue}{message_contents}")
    conversation.append({"role": "user", "content": message_contents})
    logger.info(message_contents)

    try:
        ai_response = ai_prompt(
            conversation,
            model_name,
            temperature,
            top_p,
            context_length,
            ["[Inst], </s>, <s>, (/s), [deleted], [/s], [!/s], <\\s>, [NoResponse]"] # Here, we actually exploit an old feature that removes some weird phrases it *used* to use.
                                                                                     # [NoResponse] can now be used and removed to allow Rubicon to ignore you!
        )

    except groq.GroqError as e:
        print(f"{FM.error} Rubicon::on_message || Groq Error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        logger.error(f"Rubicon::on_message || Generic Groq Error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        ai_response = f"Message loop error! Generic Groq service error. Not saying error, to preserve confidentiality.{'\n' if aggressive_error_handling else ''}"\
                                   f"{f"Aggressive error handling is enabled, so the memory will be cleared to save {bot_name}." if aggressive_error_handling else ''}"
        
        old_conversation = deepcopy(conversation)
        if aggressive_error_handling:
            conversation = deepcopy(get_replace_system_prompt())
            logger.info("Saved system prompt.")


        for module in list(get_error_modules_of_type(e).values()):
            if module[-1]:
                val = await module[0](locals()) # -1: Is a coro?

            else:
                val = module[0](locals())

            returned_locals.update(val if isinstance(val, dict) and val else {})
            should_return = returned_locals.get('should_return', False)
            message_contents = returned_locals.get('message_contents', message_contents)
            message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
            in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
            skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
            if should_return: return

    except groq.APIError as e:
        print(f"{FM.error} Rubicon::on_message || Groq API Error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        logger.error(f"Rubicon::on_message || Groq API Error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        ai_response = f"Message loop error! API error. Not saying error, to preserve confidentiality. {'\n' if aggressive_error_handling else ''}"\
                                   f"{f"Aggressive error handling is enabled, so the memory will be cleared to save {bot_name}." if aggressive_error_handling else ''}"

        old_conversation = deepcopy(conversation)
        if aggressive_error_handling:
            conversation = deepcopy(get_replace_system_prompt())
            logger.info("Saved system prompt.")


        for module in list(get_error_modules_of_type(e).values()):
            if module[-1]:
                val = await module[0](locals()) # -1: Is a coro?

            else:
                val = module[0](locals())

            returned_locals.update(val if isinstance(val, dict) and val else {})
            should_return = returned_locals.get('should_return', False)
            message_contents = returned_locals.get('message_contents', message_contents)
            message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
            in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
            skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
            if should_return: return


    except groq.RateLimitError as e:
        print(f"{FM.error} Rubicon::on_message || We're being rate limited. {type(e).__name__}: {e}\n{traceback.format_exc()}")
        logger.error(f"Rubicon::on_message || We're being rate limited. {type(e).__name__}: {e}\n{traceback.format_exc()}")
        ai_response = f"Message loop error! Rate limit reached. Not saying error, to preserve confidentiality. {'\n' if aggressive_error_handling else ''}"\
                                   f"{f"Aggressive error handling is enabled, so the memory will be cleared to save {bot_name}." if aggressive_error_handling else ''}"
        
        old_conversation = deepcopy(conversation)
        if aggressive_error_handling:
            conversation = deepcopy(get_replace_system_prompt())
            logger.info("Saved system prompt.")

 
        for module in list(get_error_modules_of_type(e).values()):
            if module[-1]:
                val = await module[0](locals()) # -1: Is a coro?

            else:
                val = module[0](locals())

            returned_locals.update(val if isinstance(val, dict) and val else {})
            should_return = returned_locals.get('should_return', False)
            message_contents = returned_locals.get('message_contents', message_contents)
            message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
            in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
            skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
            if should_return: return

    except Exception as e:
        print(f"{FM.error} Rubicon::on_message || Unknown error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        logger.error(f"Rubicon::on_message || Unknown error: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        ai_response = f"Message loop error! Unknown error. Not saying error, to preserve confidentiality. {'\n' if aggressive_error_handling else ''}"\
                                   f"{f"Aggressive error handling is enabled, so the memory will be cleared to save {bot_name}." if aggressive_error_handling else ''}"
        
        old_conversation = deepcopy(conversation)
        if aggressive_error_handling:
            conversation = deepcopy(get_replace_system_prompt())
            logger.info("Saved system prompt.")


        for module in list(get_error_modules_of_type(e).values()):
            if module[-1]:
                val = await module[0](locals()) # -1: Is a coro?

            else:
                val = module[0](locals())

            returned_locals.update(val if isinstance(val, dict) and val else {})
            should_return = returned_locals.get('should_return', False)
            message_contents = returned_locals.get('message_contents', message_contents)
            message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
            in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
            skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
            if should_return: return


    print(f"{FM.light_yellow}Rubicon:\n{ai_response[1]}")
    logger.info(f"Rubicon: {ai_response[1]}")
    conversation.append({"role": "assistant", "content": ai_response[1]})
    await message.channel.send(f"{ai_response[0] if type(ai_response) == tuple else ai_response}\n\n-# rubicon 4 **BETA**, expect many crashes and horrid issues")

    for module in list(get_staged_modules(modules_msghook, 5).values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        message_contents = returned_locals.get('message_contents', message_contents)
        message_has_special_character = returned_locals.get('message_has_special_character', message_has_special_character)
        in_all_channel = returned_locals.get('in_all_channel', in_all_channel)
        skip_general_check = returned_locals.get('skip_general_check', skip_general_check)
        if should_return: return

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
    jurigged.watch(logger=logger)

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