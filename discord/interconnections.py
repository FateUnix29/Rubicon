#-------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                     #
#                                             RUBICON LIBRARY FILE - interconnections.py                                              #
#      This file is responsible for reading/writing global variables, as well as being the main hub of information between files.     #
#  This file is necessitated because circular imports are not allowed. Instead of two files changing each other, both share this one. #
#                                                                                                                                     #
#-------------------------------------------------------------------------------------------------------------------------------------#


#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                   Imports: External Libraries                                                   ###
#-------------------------------------------------------------------------------------------------------------------------------------#

import json                                       # JSON               || JSON encoder and decoder.
import jsonc                                      # JSONC              || JSON with comments.
import logging                                    # Logging            || Functions for logging.
import groq                                       # Groq               || The Groq library. Used as the AI brains.
import requests                                   # Requests           || Functions for making HTTP requests.
import sys                                        # System             || The operating system and information about it.
import discord                                    # Discord API        || The Discord API, implemented in Python.
import os                                         # OS                 || Functions for interacting with the OS. Mostly used for pathing.
import inspect                                    # Inspect            || Functions for inspecting objects and other functions.
import functools                                  # Functions          || Functions for functions. Haha.
import jurigged                                   # Jurigged           || Functions for hot code reloading. Your eyes do not decieve you.

from os.path import \
    realpath, dirname, join as pjoin, exists      # Pathing            || Functions for pathing. Used much more commonly than the rest.

from discord import app_commands                  # Discord API        || App/slash commands.
from inspect import \
    iscoroutinefunction as iscoro                 # Inspect            || Functions for checking if a function is a coroutine.

from typing import Union                          # Typing             || For type hinting, mostly. Union, however, is literally the only way
                                                                        # To prevent a fatal error with isinstance that's compatible with my functions.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                      Imports: Source Files                                                      ###
#-------------------------------------------------------------------------------------------------------------------------------------#

from resources.other.colors import *              # ANSI Color Coding  || Terminal color coding.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                Initialization, Some Basic Globals                                               ### 
#-------------------------------------------------------------------------------------------------------------------------------------#

# This file does some of it's own management along with the globals.
# One of those is json. Another is logging initialization. Basically, everything is here.

file_directory = dirname(realpath(__file__))                                           # Directory we're in.
log_file = pjoin(file_directory, "rubicon-discord.log")                                # Log file location.

class RubiconError(Exception):
    """Rubicon's base error class."""
    pass

class ConflictError(RubiconError):
    """A module has a conflict with another module."""
    con_1_file_name: str
    con_2_file_name: str

    def __init__(self, message: str, con_1_file_name: str, con_2_file_name: str) -> None:
        super().__init__(f"{message} (file 1: {con_1_file_name}, file 2: {con_2_file_name})")
        self.con_1_file_name = con_1_file_name
        self.con_2_file_name = con_2_file_name

if exists(log_file): os.remove(log_file) # Remove log file if it exists. By default, logging uses append.

logger = logging.getLogger("rubicon-discord")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file, encoding="utf-8", errors="ignore")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

try:
    with open(pjoin(file_directory, "keynames.json"), "r") as file:
        keynames = json.load(file)
        logger.info("Successfully read keynames file.")
except FileNotFoundError:
    FM.header_error("Fatal Exception: Unable to read keynames file",
    f"Rubicon couldn't find it's keynames file. Perhaps you deleted it, didn't clone/move it to the base directory, or moved it somewhere else?")
    logger.critical("Exiting safely: Unable to read keynames file. (keynames file not found)")
    sys.exit(1)

if len(keynames) != 2:
    FM.header_error("Fatal Exception: Invalid keynames file",
    f"Keynames file had an invalid amount of keys. It should have exactly 2 keys, but it had {len(keynames)} key(s).")
    logger.critical("Exiting safely: Invalid keynames file. (keynames had an invalid amount of keys)")
    sys.exit(1)

discord_token = os.getenv(keynames["DISCORD_BOT_TOKEN"]) or None
groq_api_key = os.getenv(keynames["GROQ_API_KEY"]) or None

#logger.debug(f"Token information: {discord_token}, {groq_api_key}, {keynames}")

if discord_token is None or groq_api_key is None:
    FM.header_error("Fatal Exception: Invalid keynames file",
    f"Keynames file has an invalid key(s). Please check that the specified environment variables exist.")
    logger.critical("Exiting safely: Invalid keynames file. (discord_token or groq_api_key was null)")
    sys.exit(1)

model_name_DEFAULT = "llama3-70b-8192"

try:
    with open(pjoin(file_directory, "config.jsonc"), "r") as file:
        config_dict = jsonc.load(file)
        logger.info("Successfully read config file.")
except FileNotFoundError:
    FM.header_error("Fatal Exception: Unable to read config file",
    f"Rubicon couldn't find it's config file. Perhaps you deleted it, didn't clone/move it to the base directory, or moved it somewhere else?")
    logger.critical("Exiting safely: Unable to read config file. (config file not found)")
    sys.exit(1)

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                          Functions PT1                                                          ###
#-------------------------------------------------------------------------------------------------------------------------------------#

def get_valid_groq_model(model: str = "llama3-70b-8192") -> str:
    """Check if the model name provided is valid, and return it if so. Otherwise, return the default model name global.
    
    :param model: The model name to check.
    :type model: str
    
    :return: The valid model name, or the default if an error occured.
    :rtype: str"""

    _url = "https://api.groq.com/openai/v1/models"
    _headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(_url, headers=_headers).json()

    for model_dict in response["data"]:
        if model_dict["id"] == model:
            logger.info(f"interconnections.py::get_valid_groq_model || Grabbed valid model '{model}'.")
            model_response = model_dict["id"]
            return model_response
        else:
            continue

    logger.error(f"interconnections.py::get_valid_groq_model || Invalid model '{model}'.")
    return model_name_DEFAULT

def fetch_current_sibling_count() -> int:
    """Grab the current sibling count within the siblings.txt file.
    
    :return: The current sibling count, or the default if an error occured.
    :rtype: int"""

    try:
        with open(pjoin(file_directory, "siblings.txt"), "r") as file:
            logger.info("interconnections.py::fetch_current_sibling_count || Grabbed current sibling count.")
            return int(file.read())
    except FileNotFoundError:
        logger.error("interconnections.py::fetch_current_sibling_count || Unable to find siblings file. Creating file...")
        try:
            with open(pjoin(file_directory, "siblings.txt"), "w") as file:
                file.write(str(default_sibling_count))
            logger.info("interconnections.py::fetch_current_sibling_count || Created new siblings file.")
        except PermissionError:
            logger.error("interconnections.py::fetch_current_sibling_count || Unable to write to siblings file. Permissions error.") # NOT fatal.
        return default_sibling_count

def todo(message: str) -> None:
    """Warn that something has yet to be implemented, without crashing the program.
    
    :param message: The message to log.
    :type message: str"""

    logger.warning(f"interconnections.py::todo || '{message}'")
    # Raise no errors.

def todo_fatal(message: str) -> None:
    """Warn that something has yet to be implemented, crashing the program.
    
    :param message: The message to log.
    :type message: str"""

    logger.critical(f"interconnections.py::todo_fatal || '{message}'")
    sys.exit(1)

def validity_check(value: any, correct_types: Union[type, tuple[type]], crash_message: str | None = None, value_name: str = ""):
    """Check if the value is of the correct type. Crash if not.
    
    :param value: The value to check.
    :type value: Any
    :param correct_type: The type to check for.
    :type correct_type: Type | Tuple[Type]
    :param crash_message: The message to print in the event of a crash.
    :type crash_message: str | None
    :param value_name: The name of the value being checked.
    :type value_name: str

    :return: The value if it is of the correct type.
    :rtype: Any"""
    
    if not isinstance(value, correct_types):
        if crash_message is None:
            crash_message = f"Bad configuration file: {value_name} must be of type {correct_types}, but instead the value was '{value}' with type {type(value)}."
        logger.critical(f"interconnections.py::validity_check || '{crash_message}'")
        sys.exit(1)
    else:
        return value
    
def get_watchlist() -> list[dict]:
    """Get the contents of the watchlist.json file, representing every message from tracked users.
    
    :return: The contents of the watchlist.json file.
    :rtype: list[dict]"""

    try:
        with open(pjoin(file_directory, "watchlist.json"), "r") as file:
            logger.info("interconnections.py::get_watchlist || Grabbed watchlist.")
            return json.load(file)
    except FileNotFoundError:
        logger.error("interconnections.py::get_watchlist || Unable to find watchlist file. Creating file...")
        try:
            with open(pjoin(file_directory, "watchlist.json"), "w") as file:
                json.dump([], file, indent=4)
            logger.info("interconnections.py::get_watchlist || Created new watchlist file.")
        except PermissionError:
            logger.error("interconnections.py::get_watchlist || Unable to write to watchlist file. Permissions error.") # NOT fatal.
        return []
    
def get_replace_system_prompt() -> list[dict[str, str]]:
    """Get the contents of base.json, which contains the starting-out conversation.
    
    :return: The contents of base.json.
    :rtype: list[dict[str, str]]"""

    try:
        with open(pjoin(file_directory, "base.json"), "r") as file:
            logger.info("interconnections.py::get_replace_system_prompt || Grabbed base prompt.")
            jsondict = json.load(file)
            for entry in jsondict:
                entry["content"] = entry["content"].replace(f"{{BOT_NAME}}", bot_name)
            return jsondict
    except FileNotFoundError:
        logger.error("interconnections.py::get_replace_system_prompt || Unable to find base file. Creating file...")
        try:
            with open(pjoin(file_directory, "base.json"), "w") as file:
                json.dump([{"role": "system", "content": ""}], file, indent=4)
            logger.info("interconnections.py::get_replace_system_prompt || Created new base file.")
        except PermissionError:
            logger.error("interconnections.py::get_replace_system_prompt || Unable to write to base file. Permissions error.")
        logger.exception("interconnections.py::get_replace_system_prompt || Without the base system prompt, the program will be useless. Crashing.")
        sys.exit(1)

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                             Globals                                                             ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# AI
logger.debug("interconnections.py || AI globals...")
bot_name =                     validity_check(config_dict["bot_name"], str, value_name="bot_name")
temperature =                  validity_check(config_dict["temperature"], float, value_name="temperature")
top_p =                        validity_check(config_dict["top_p"], float, value_name="top_p")
context_length =               validity_check(config_dict["context_len"], int, value_name="context_len")
random_message_chance =        validity_check(config_dict["random_message_chance"], int, value_name="random_message_chance")
default_sibling_count =        validity_check(config_dict["default_sibling_count"], int, value_name="default_sibling_count")
model_name =                   get_valid_groq_model(validity_check(config_dict["model_name"], str, value_name="model_name"))

# AI (Internal use; non-configured)
logger.debug("interconnections.py || Internal use AI globals...")
sibling_count = fetch_current_sibling_count()
conversation = get_replace_system_prompt()
conversation[0]["content"] = conversation[0]["content"].replace(f"{{{{bot_name}}}}", bot_name) # he he he he hah hah hah

# Discord
logger.debug("interconnections.py || Discord globals...")
respond_by_default =           validity_check(config_dict["respond_by_default"], bool, value_name="respond_by_default")
special_character =            validity_check(config_dict["special_character"], str, value_name="special_character")
crashes_are_siblings =         validity_check(config_dict["crashes_are_siblings"], bool, value_name="crashes_are_siblings")
universal_sync =               validity_check(config_dict["universal_sync"], bool, value_name="universal_sync")
target_server_for_sync =       validity_check(config_dict["target_server_for_sync"], Union[int, None], value_name="target_server_for_sync")

aggressive_error_handling =    validity_check(config_dict["aggressive_error_handling"], bool, value_name="aggressive_error_handling")
respond_in_every_channel =     validity_check(config_dict["respond_in_every_channel"], bool, value_name="respond_in_every_channel")

home_channel_name =            validity_check(config_dict["home_channel_name"], str, value_name="home_channel_name")
system_channel_name =          validity_check(config_dict["system_channel_name"], str, value_name="system_channel_name")
all_channel_name =             validity_check(config_dict["all_channel_name"], str, value_name="all_channel_name")

all_channel_enabled =          validity_check(config_dict["all_channel_enabled"], bool, value_name="all_channel_enabled")

dev_mode =                     validity_check(config_dict["dev_mode"], bool, value_name="dev_mode")
notify_on_boot =               validity_check(config_dict["notify_on_boot"], bool, value_name="notify_on_boot")

role_rubicontrol =             validity_check(config_dict["rubicon_control_role"], str, value_name="rubicon_control_role")
role_rubielevated =            validity_check(config_dict["rubicon_elevated_role"], str, value_name="rubicon_elevated_role")
role_rubiboot =                validity_check(config_dict["rubicon_boot_role"], str, value_name="rubicon_boot_role")
role_norubi =                  validity_check(config_dict["no_rubicon_role"], str, value_name="no_rubicon_role")

lockdown =                     validity_check(config_dict["lockdown"], bool, value_name="lockdown")
ids_rubicontrol =              validity_check(config_dict["ids_lockdown_control"], list, value_name="ids_lockdown_control")
ids_rubielevated =             validity_check(config_dict["ids_lockdown_elevated"], list, value_name="ids_lockdown_elevated")

# Discord (Internal use; non-configured)
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)
watchlist_log = watchlist_log = get_watchlist()

# Other
version =                      validity_check(config_dict["version"], str, value_name="version")

# Other (Internal use; non-configured)
logger.debug("interconnections.py || Specific internal globals...")
modules_fncall = {
    # This is going to require a lot of explanation, so here we go.
    # What is this dict for?
    # It is for source files that Rubicon calls 'modules', not to be confused with *Python* modules.
    # A module in Rubicon's terms is a file that Rubicon has the ability to run on demand. Basically, plug-and-play abilities.
    # I've also decided that Rubicon should have internal modules that are there by default, but can TECHNICALLY be removed, in place of the old in-place methods.
    # These modules can include commands, function calls for Rubicon's AI systems, etc.
    # It uses a complicated decorator system, but when using it from the outside, it should be easy to understand.
    # This dict stores the functions from these modules with a specific format, but in theory, it stores their RAM locations and the functions can be called without importing them.

    # What do I mean when I say these modules will replace in-place functions?
    # The API allows for these functions to be wrapped as an app command, and then the function will be called when the command is called.
    # It will be complicated and will likely mess with globals.

    # That explains all of the dictionaries, but this dictionary in specific is for Rubicon function calls.
}

modules_msghook = {
    # This module dict is called during specific parts of the on_message function.
}

modules_readyhook = {
    # This module dict is called during specific parts of the on_ready function.
}

modules_generic = {
    # This module dict is called during any state of on_... function, excluding on_ready and on_message.
    # This is for things like on_error, on_command_error, on_guild_join, etc.
}

modules_errhook = {
    # This module dict is called during on_message() error handling.
}

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                        Functions (Proper)                                                       ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# This includes decorators.

def rubicon_fncall(custom_name: str | None = None):
    """Rubicon function call - Functions marked with this decorator will be accessible to Rubicon as a function call.
    The decorated function will always be called with the current conversation as the first argument.
    **Function calls do not support kwargs.**

    :param custom_name: The name of the function. Defaults to the function's name.
    :type custom_name: str
    :return: The function wrapped as a function call.
    :rtype: function"""

    # MODULES_FNCALL DICT FORMAT:
    # "name_for_rubicon": [function, [arguments (minus conversation)], file, is coro?]

    # Modules are passed the conversation argument so they may give the results back to Rubicon or modify the conversation in any other way.
    # They are expected to keep track of the state of Rubicon themselves, however, if they are to error out under specific conditions/states.
    # Under no circumstances are they allowed to crash the program or script.

    def decorator(func):
        nonlocal custom_name # screw you, scopes
        if not custom_name:
            custom_name = func.__name__
        file = func.__code__.co_filename

        # Add this function to the modules dict.
        modules_fncall[custom_name] = [func, inspect.getfullargspec(func).args[1:], file, iscoro(func)] # Conversation given automatically, used or not
        logger.info(f"interconnections.py::rubicon_fncall || {'Added' if not custom_name in modules_fncall else 'Replaced'} function call {'to' if not custom_name in modules_fncall else 'in'} Rubicon: {custom_name}")
        @functools.wraps(func)
        def wrapper(conversation, *args):
            
            logger.debug(f"interconnections.py::rubicon_fncall || Rubicon called function: {custom_name}")
            try:
                return func(conversation, *args)
            except Exception as e:
                logger.error(f"interconnections.py::rubicon_fncall || Error in {custom_name}: {type(e).__name__}:{e}")
                # CANNOT crash Rubicon. at ALL costs.
                return f"Function {custom_name} raised an error: {type(e).__name__}: {e}"
        return wrapper
    return decorator

def rubicon_msghook(stage: int = 5):
    """Rubicon message hook - Functions marked with this decorator will be called in one of 5 stages of the on_message function.
    The decorated function will always be called with the locals of the event it is hooked to as the first argument.
    
    :param stage: The stage of the on_message function. Defaults to 5, for latest stage. 1 would be earliest.
    :type stage: int
    :return: The function wrapped as a message hook.
    :rtype: function"""

    def decorator(func):
        custom_name = func.__name__
        file = func.__code__.co_filename

        # Add this function to the modules dict.
        modules_msghook[custom_name] = [func, stage, inspect.getfullargspec(func).args[1:], file, iscoro(func)] # Local variables given automatically, used or not
        logger.info(f"interconnections.py::rubicon_msghook || {'Added' if not custom_name in modules_msghook else 'Replaced'} message hook {'to' if not custom_name in modules_msghook else 'in'} Rubicon: {custom_name}")
        @functools.wraps(func)
        def wrapper(locals, *args):
            
            logger.debug(f"interconnections.py::rubicon_msghook || Function hooked to on_message called: {custom_name} (called at stage {stage})")
            try:
                return func(locals, *args)
            except Exception as e:
                logger.error(f"interconnections.py::rubicon_msghook || Error in {custom_name}: {type(e).__name__}:{e}")
                # CANNOT crash Rubicon. at ALL costs. ESPECIALLY not the client.
                return f"Function {custom_name} raised an error: {type(e).__name__}: {e}"
        return wrapper
    return decorator

def rubicon_readyhook(stage: int = 3):
    """Rubicon ready hook - Functions marked with this decorator will be called in one of 3 stages of the on_ready function.
    The decorated function will always be called with the locals of the event it is hooked to as the first argument.
    
    :param stage: The stage of the on_ready function. Defaults to 3, for latest stage. 1 would be earliest.
    :type stage: int
    :return: The function wrapped as a ready hook.
    :rtype: function"""
    def decorator(func):
        custom_name = func.__name__
        file = func.__code__.co_filename

        # Add this function to the modules dict.
        modules_readyhook[custom_name] = [func, stage, inspect.getfullargspec(func).args[1:], file, iscoro(func)] # Local variables given automatically, used or not
        logger.info(f"interconnections.py::rubicon_readyhook || {'Added' if not custom_name in modules_readyhook else 'Replaced'} ready hook {'to' if not custom_name in modules_readyhook else 'in'} Rubicon: {custom_name}")
        @functools.wraps(func)
        def wrapper(locals, *args):
            
            logger.debug(f"interconnections.py::rubicon_readyhook || Function hooked to on_ready called: {custom_name} (called at stage {stage})")
            try:
                return func(locals, *args)
            except Exception as e:
                logger.error(f"interconnections.py::rubicon_readyhook || Error in {custom_name}: {type(e).__name__}:{e}")
                # CANNOT crash Rubicon. at ALL costs. ESPECIALLY not the client.
                return f"Function {custom_name} raised an error: {type(e).__name__}: {e}"
        return wrapper
    return decorator

def rubicon_generichook(event: str, *args, **kwargs):
    """Generic Rubicon hook. Incredibly experimental and 100% not guaranteed to work. Use at risk. This assumes you've seen the other hooks' docstrings before.
    The decorated function will always be called with the locals of the event it is hooked to as the first argument.
    
    :param event: A string. It must match the exact function name of the event. Examples are on_ready, on_message, on_guild_join, etc.
    :type event: str
    
    :raise Exception: If the event is unknown. on_ready and on_message are also unknown as they are handled by their respective decorators.

    This decorator also accepts *args and **kwargs. A good example would be stage=5, if applicable. Ensure you read the documentation on what events are present,
    and what arguments they may have.
    
    :return: The function wrapped as a generic hook.
    :rtype: function"""
    def decorator(func):

        # Add this function to the modules dict.
        if not event in modules_generic:
            logger.critical(f"interconnections.py::rubicon_generichook || Unknown event: {event}")
            raise Exception(f"Unknown generic event: {event}")
        
        modules_generic[event][func.__name__] = [func, args, kwargs, inspect.getfullargspec(func).args[1:], file, iscoro(func)] # Local variables given automatically, used or not
        logger.info(f"interconnections.py::rubicon_generichook || {'Added' if not func.__name__ in modules_generic else 'Replaced'} generic ({event}) hook {'to' if not func.__name__ in modules_generic else 'in'} Rubicon: {func.__name__}")
        @functools.wraps(func)
        def wrapper(*args):
            
            logger.debug(f"interconnections.py::rubicon_generichook || Function hooked to {event} called: {func.__name__}")
            try:
                return func(*args)
            except Exception as e:
                logger.error(f"interconnections.py::rubicon_generichook || Error in {func.__name__}: {type(e).__name__}:{e}")
                # CANNOT crash Rubicon. at ALL costs. ESPECIALLY not the client.
                return f"Function {func.__name__} raised an error: {type(e).__name__}: {e}"
        return wrapper
    return decorator

def mark_generic_event():
    """Mark this function as a generic event. This allows modules to hook to it. Name must start with on_, and it must be a coro.
    
    :raise Exception: If the function does not start with on_ or if it is not a coroutine.

    :return: The function, pretty much unchanged.
    :rtype: function"""

    def decorator(func):
        if not func.__name__.startswith("on_"):
            logger.critical(f"interconnections.py::mark_generic_event || Function {func.__name__} does not start with 'on_'")
            raise Exception(f"Function {func.__name__} does not start with 'on_'")
        if not iscoro(func):
            logger.critical(f"interconnections.py::mark_generic_event || Function {func.__name__} is not a coroutine")
            raise Exception(f"Function {func.__name__} is not a coroutine")

        modules_generic[func.__name__] = {}
        logger.info(f"interconnections.py::mark_generic_event || Marked {func.__name__} as a generic event")
        @functools.wraps(func)
        def wrapper(*args):
            return func(*args)
        return wrapper
    return decorator

def rubicon_information(information: str):
    """Add any string to Rubicon's system prompt. Very useful to tell it what's going on."""
    # While it was originally going to be a decorator, why does it need to be a decorator

    conversation[0]["content"] += information

def rubicon_msghook_err(error_class: Exception):
    """A specialized hook that hooks into error handling within Rubicon's message hook, incase the AI fails.
    The decorated function will always be called with the locals of the event it is hooked to as the first argument.
    
    :param error_class: The class of the error to match. Can be literally any error, as Rubicon has a catch-all.
    :type error_class: Exception
    
    :return: The function wrapped as a hook.
    :rtype: function"""
    def decorator(func):
        # Add this function to the modules dict.
        if not type(error_class).__name__ in modules_errhook:
            modules_errhook[type(error_class).__name__] = []
        modules_errhook[type(error_class).__name__].append(func, inspect.getfullargspec(func).args[1:], file, iscoro(func))
        logger.info(f"interconnections.py::rubicon_msghook_err || Added error hook {'to' if not func.__name__ in modules_errhook else 'in'} Rubicon: {func.__name__}")

        @functools.wraps(func)
        def wrapper(locals, *args):
            logger.debug(f"interconnections.py::rubicon_msghook_err || Function hooked to on_message error handling called: {func.__name__}")
            try:
                return func(locals, *args)
            except Exception as e:
                logger.error(f"interconnections.py::rubicon_msghook_err || Error in {func.__name__}: {type(e).__name__}:{e}")
                # CANNOT crash Rubicon. at ALL costs. ESPECIALLY not the client.
                return f"Function {func.__name__} raised an error: {type(e).__name__}: {e}"
        return wrapper
    return decorator

def get_staged_modules(module_type: dict, stage: int) -> dict:
    """Get all modules within a specific module dict with the specified stage.
    
    :param module_type: The module dict to search.
    :type module_type: dict
    :param stage: The stage of the modules to get.
    :type stage: int
    :return: The modules with the specified stage.
    :rtype: dict
    """
    return {k: v for k, v in module_type.items() if v[1] == stage}

def get_modules_of_parameters(fn_name: str) -> dict:
    """Get all generic modules with the specified event name.
    
    :param fn_name: The event name to search for.
    :type fn_name: str
    
    :raise NameError: The event name is not a generic event. (Unknown event.)
    
    :return: The generic modules with the specified event name.
    :rtype: dict"""

    if fn_name not in modules_generic:
        logger.critical(f"interconnections.py::get_modules_of_parameters || Unknown event: {fn_name}")
        raise NameError(f"Unknown event: {fn_name}")
    return modules_generic[fn_name]

def get_error_modules_of_type(error_class: Exception) -> dict:
    """Get all error modules with the specified error class.
    
    :param error_class: The error class to search for.
    :type error_class: Exception
    
    :raise NameError: The error class is not an error class. (Unknown error class.)
    
    :return: The error modules with the specified error class.
    :rtype: dict"""

    if type(error_class).__name__ not in modules_errhook:
        logger.critical(f"interconnections.py::get_error_modules_of_type || Unknown error class: {type(error_class).__name__}")
        raise NameError(f"Unknown error class: {type(error_class).__name__}")
    return modules_errhook[type(error_class).__name__]

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                        Discord Functions                                                        ###
#-------------------------------------------------------------------------------------------------------------------------------------#

@mark_generic_event()
@client.event
async def on_error(event, *args, **kwargs):
    for _, module in get_modules_of_parameters("on_error").items():
        if module[-1]: await module[0](locals()) # -1: Is a coro?
        else:          module[0](locals())

def get_guilds_with_channel_name(name: str = "rubicon-general") -> list[discord.Guild] | None:
    """Get all guilds with the specified channel name.
    
    :param name: The channel name to search for.
    :type name: str
    
    :return: The guilds with the specified channel name, or None if not found.
    :rtype: list[discord.Guild] | None"""
    return [guild for guild in client.guilds if name in [channel.name for channel in guild.text_channels]] # Inefficiency at it's finest

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                             Cleanup                                                             ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# Close logging file
file_handler.close()