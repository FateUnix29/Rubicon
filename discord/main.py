###############################################################################################################################################
##                                                                                                                                           ##
##                                                            RUBICON - V:3.14.1.1                                                           ##
##                                                Your absolutely nuts silicion-based friend.                                                ##
##                                                                                                                                           ##
##                                           Created by Destiny (Copper (FateUnix29), @destiny_29)                                           ##
##                                            Licensed under GNU GPL v3. See LICENSE for details.                                            ##
##                                                                                                                                           ##
##                                       Find Rubicon on GitHub: https://github.com/FateUnix29/Rubicon                                       ##
##                                                                                                                                           ##
###############################################################################################################################################

###  Imports  ###

import discord                                                 # Discord API.
from discord import app_commands                               # This allows for slash commands.
import groq                                                    # Groq API. This is the AI part of Rubicon.
import random, os                                              # Random and OS.
#import threading                                              # As of Rubicon V:3.*, we are attempting to use threads to have CLI input and speed up the bot.
import sys                                                     # System.
from os import getenv                                          # Environment variables, because as of V:3.*, I finally bother to use non-hardcoded (and slightly encrypted) keys.
import utilities as utils                                      # Utilities; Functions and classes.
from utilities import print, FM                                # These two specifically should be accessed as if they were declared in the main file (this file).
import json                                                    # JSON. For chat history saving and reading.
from copy import deepcopy                                      # Deepcopy. Mainly for chat history.
import traceback                                               # Traceback.

###   Init    ###

# For some explanation on this section, there are a few things that I'd like to do before everything else.

# Get python interpreter version
ver = sys.version_info
ver = f"{ver.major}.{ver.minor}.{ver.micro} ({ver.releaselevel})"
expected = "3.12.6 (final)"
if ver != expected:
    print(f"\n{FM.light_yellow}Small warning:\nYour Python interpreter does not match that of what Rubicon was developed with.\n\
This, of course, may cause errors. The version of your Python interpreter is {ver}, and Rubicon was developed with {expected}.\n")
    if sys.version_info.minor < 10:
        print(f"{FM.light_red}Attention: You are using Python 3.9x or lower. This *will* cause errors which will likely stop Rubicon in it's tracks.")

### Constants ###

_ver = "3.14.1.1"

###  Globals  ###

# Basic variables
bot_name = "Rubicon"                                     # Name of the bot/AI.

# AI-specific variables
current_model = "llama3-70b-8192"                        # Name of the current model. Heavily influences AI behavior.
temperature = 0.2                                        # Model temperature. Temperature is a number that influences how likely it is to choose less-likely words.
top_p = 1                                                # Top-p. Not too sure what this does, so no description. Change this or temperature, but probably not both.
maximum_tokens = 8192                                    # Maximum context length. This is the maximum number of tokens the AI can remember. Default is 8192, the max for llama3-70b-8192.
last_ai_message = None                                   # I absolutely doubt that we'll need this, but it's here.
random_message_chance = 50                               # The chance that a random message will be sent in addition to the AI's response. Default is 50 (1 in 50).
sibling_count = 0                                        # Number of siblings if the file cannot be read.
old_sibling_count = sibling_count                        # Internal use only.

ai_models = ["llama3-7b-8192", 
             "gemma-7b-it", 
             "llama3-70b-8192", 
             "mixtral-8x7b-32768", ]                     # List of all available models. Users will have to pick between these.

# Discord-specific variables
respond_to_messages = True                               # Does Rubicon respond to messages?
special_character = "^"                                  # Special character. Putting at the start of a message will either send it to Rubicon or do the inverse, depending on below var.
respond_by_default = True                                # Does Rubicon respond to messages by default? Variable above will exclude messages if so, else include.
increment_siblings_on_die = True                         # If Rubicon's AI process crashes, does it increment it's sibling count?
sync_commands_to_all_servers = True                      # Does Rubicon sync it's commands to all servers it is in?
server_to_sync_to = discord.Object(1247723267029074002)  # List of servers to sync it's commands to if not syncing to all servers.
send_message_everywhere = False                          # Does Rubicon send it's response across all servers, giving the look of it seeing things that don't exist?
last_message = None                                      # Incase we need it.
aggressive_error_handling = True                         # Does Rubicon attempt to clear it's memory with no confirmation if it encounters an error?
respond_in_all_channels = False                          # Does Rubicon respond to a message in any channel? If false, only responds to messages in rubicon-general.
target_channel_name = "rubicon-general"                  # If respond_in_all_channels is False, this is the name of the channel to respond in.
conjoined_channel_name = "rubicon-all"                   # Same as target_channel_name, but it will send messages from this channel in other servers to every other server's rubicon-all.

dev_mode = False                                         # Does Rubicon run in dev mode? Meaning, it doesn't send out boot pings.

rubicon_control_role = "Rubicon Control"                 # Control role.
rubicon_elevated_role = "Rubicon Elevated"               # Elevated role.
no_rubicon_role = "No Rubicon"                           # No Rubicon role.
rubicon_boot_role = "Rubicon Boot Ping"                  # Boot ping.

rubicon_lockdown = False                                 # Is Rubicon locked down? In locked down mode, it doesn't obey any roles besides No Rubicon and Rubicon Boot Ping.
                                                         # This is useful for when Rubicon is placed in a server that has staff that can add Rubicon Control & Elevated to themselves.
                                                         # And even, add it to others.

# D-Control-specific variables
target_channel = None                                    # Target channel.
target_guild = None                                      # Target guild.

# Variables that are decided by code
discord_token = getenv("DT") # Short for 'Discord Token'.
groq_api_key =  getenv("GK") # Short for 'Groq Key'.
# Client object
client = discord.Client(intents=discord.Intents.all())
# It's commands
tree = app_commands.CommandTree(client=client)

# The directory of this file.
file_dirname = os.path.dirname(os.path.realpath(__file__))

# Checks and bounds: Do the specified variables here make sense?
if current_model not in ai_models:
    FM.header_warn("Model not found", "The model specified as the default model for Rubicon is not found. Defaulting to 'llama3-70b-8192'.")
    current_model = "llama3-70b-8192" # Default model.

### Functions ###
# General
def rubicon_welcome_message(extra_newline: bool = False):
    """Prints a big welcome message to the screen.
    
    Args:
        extra_newline (bool, optional): Add an extra newline to the end. Defaults to False."""
    count = 60
    print(f"{FM.light_yellow}{'-'*count}", reset_color=False)
    print(f"|{' '*(count-2)}|", reset_color=False)
    string_to_print_1 = f"RUBICON - V:{_ver}"
    string_to_print_2 = "Your absolutely nuts silicon-based friend."
    spaces_string_1 = ((count-2) - len(string_to_print_1)) // 2
    if spaces_string_1 // 2 == 0:
        #print("even")
        spaces_string_12 = spaces_string_1 + 1
    else:
        #print("odd")
        spaces_string_12 = spaces_string_1
    #print(spaces_string_1, spaces_string_12)
    print(f"|{' '*spaces_string_1}{string_to_print_1}{' '*(spaces_string_12)}|", reset_color=False)
    spaces_string_2 = ((count-2) - len(string_to_print_2)) // 2
    print(f"|{' '*spaces_string_2}{string_to_print_2}{' '*spaces_string_2}|", reset_color=False)
    print(f"|{' '*(count-2)}|", reset_color=False)
    print(f"{'-'*count}{'\n' if extra_newline else ''}")

# AI
def grab_siblings(set_both: bool = False):
    global sibling_count, old_sibling_count
    try:
        with open(os.path.join(file_dirname, "siblings.txt"), "r") as f:
            new_sibling_count = int(f.read())
            if not set_both:
                old_sibling_count = sibling_count
                sibling_count = new_sibling_count
            else:
                old_sibling_count, sibling_count = new_sibling_count, new_sibling_count
    except FileNotFoundError:
        print(f"{FM.warning} Cannot find siblings file.")
    except PermissionError:
        print(f"{FM.warning} Permission denied to siblings file.")
    except IsADirectoryError:
        print(f"{FM.warning} Siblings file is a directory.")
    except Exception as e:
        print(f"{FM.warning} grab_siblings() Unknown error: {type(e).__name__}: {e}")

def write_siblings():
    global sibling_count
    try:
        with open(os.path.join(file_dirname, "siblings.txt"), "w") as f:
            f.write(str(sibling_count))
    except PermissionError:
        print(f"{FM.warning} Permission denied to siblings file.")
    except IsADirectoryError:
        print(f"{FM.warning} Siblings file is a directory.")
    except Exception as e:
        print(f"{FM.warning} write_siblings() Unknown error: {type(e).__name__}: {e}")

grab_siblings(True)


def save_memory(memory: list[dict[str, str]], path: str = "memory.json", protect_path: bool = True) -> str:
    if os.path.dirname(path) == "": path = os.path.join(file_dirname, "memories", path)
    if protect_path:
        # Disallow any path traversal. Lock dirname to memory file directory. 
        if os.path.dirname(path) != os.path.join(file_dirname, "memories"):
            return "Operation not permitted. (Access to specified path denied)"
    try:
        with open(path, "w") as f:
            # Previously, the memory was a very specifically written custom format.
            # As of Rubicon V:3.*, the memory is now a JSON file.
            json.dump(memory, f, indent=4)
        return "Saved memory successfully."
    except IsADirectoryError:
        return "Operation failed. (Path is a directory)"
    except PermissionError:
        return "Operation failed. (Permission denied)"
    except OSError:
        return "Operation failed. (Invalid path)"
    except Exception as e:
        return f"Operation failed. (General exception ('{type(e).__name__}: {e}'))"
    
def read_memory(path: str = "memory.json", protect_path: bool = True) -> str:
    if os.path.dirname(path) == "": path = os.path.join(file_dirname, "memories", path)
    if protect_path:
        # Disallow any path traversal. Lock dirname to memory file directory.
        if os.path.dirname(path) != os.path.join(file_dirname, "memories"):
            return "Operation not permitted. (Access to specified path denied)"
    try:
        with open(path, "r") as f:
            memory = json.load(f)
        return memory
    except IsADirectoryError:
        return "Operation failed. (Path is a directory)"
    except PermissionError:
        return "Operation failed. (Permission denied)"
    except FileNotFoundError:
        return "Operation failed. (File not found)"
    except OSError:
        return "Operation failed. (Invalid path)"
    except Exception as e:
        return f"Operation failed. (General exception ('{type(e).__name__}: {e}'))"
    
# Non-Function: Late initialization. Load the base system prompt.
conversation = read_memory(os.path.join(file_dirname, 'base.json'), protect_path=False)
def fix_conversation(old_sib_count: int, new_sib_count: int):
    global conversation
    replace_words = {
        f"{{{{bot_name}}}}": bot_name,

        f"-: Sometimes you wish you had siblings.": "-: Sometimes you wish you had siblings." if new_sib_count == 0 else f"-: You have {new_sib_count} older twin sibling{'s' if new_sib_count > 1 else ''} named {bot_name} also named Rubicon that you haven't spoken to in a while. Sometimes you wonder where they went.",

        f"-: You have {old_sib_count} older twin sibling{'s' if old_sib_count > 1 else ''} named {bot_name}.": f"-: You have {new_sib_count} older twin sibling{'s' if new_sib_count > 1 else ''} named {bot_name}." if new_sib_count > 0 else f"-: Sometimes you wish you had siblings.",

    }
    for word in replace_words: conversation[0]["content"] = conversation[0]["content"].replace(word, replace_words[word])
fix_conversation(sibling_count, sibling_count)
restore_point = deepcopy(conversation)

# Discord (Event Handlers)

@client.event
async def on_ready():
    rubicon_welcome_message(extra_newline=True)
    print(f"{FM.success} Logged in as {client.user} ({client.user.id})")
    await leave_all_unauthorized_guilds(client.guilds)
    guilds_general = guilds_with_rubicongeneral()
    guilds_sys = guilds_with_rubiconsystem()
    for guild in guilds_general:
        # guilds_general takes the priority and thus is why it is the one being iterated over.
        # It is a fallback for system messages.
        channel_to_send_to = None
        if guild in guilds_sys: channel_to_send_to = discord.utils.get(guild.text_channels, name="rubicon-system-messages") # If we have a system channel available, use it.
        else: channel_to_send_to = discord.utils.get(guild.text_channels, name="rubicon-general") # Otherwise, use the rubicon general channel.
        if not channel_to_send_to: print(f"{FM.warning} This server has no #rubicon-general channel or #rubicon-system-messages channel. Rubicon cannot send a boot message.")        
        # Create a boot embed.
        boot_embed = discord.Embed(title="Rubicon Started", description=f"Rubicon (v{_ver}) has woken up and booted. You may now interact with it.", color=0xffc919)
        # Search for the boot role.
        boot_role = discord.utils.get(guild.roles, name=rubicon_boot_role)
        boot_ping_txt = f"<@&{boot_role.id}>" if boot_role else "No Rubicon Boot Ping role found, please consider adding one (or asking staff to add one) \
if you or others wish to be pinged when I start."
        if not boot_role: print(f"{FM.warning} Server '{guild.name}' ({guild.id}) has no Rubicon Boot Ping role. Please consider adding one (or asking staff to add one).")
        if dev_mode: boot_ping_txt = "I'm in developer mode, so I won't ping you when I start!" # In dev mode, don't ping anyone.
        if channel_to_send_to: await channel_to_send_to.send(boot_ping_txt, embed=boot_embed)
    print(f"{FM.trying} Attempting to sync to specified guilds...")
    if not sync_commands_to_all_servers:
        await tree.sync(guild=server_to_sync_to)
    else:
        await tree.sync()
    print(f"{FM.success} Synced commands to specified guilds.")
    # Reset username.
    if not client.user.name == bot_name:
        await client.user.edit(username=bot_name)
        print(f"{FM.success} Reset username to '{bot_name}'.")
    print("-" * 100)

@client.event
async def on_guild_join(guild: discord.Guild):
    print(f"{FM.warning} Joined guild '{guild.name}' ({guild.id}).")
    # Send a message to the first channel found.
    # Check if this is in authorized guilds
    if not guild.id in get_guilds_id_from_file():
        guild.text_channels[0].send("Unauthorized join activity. Sorry, but I'm leaving now.")
        guild.leave()

@client.event
async def on_message(message):
    # Globals we wish to modify, because Python will simply shadow them if we don't declare them.
    global last_message, conversation, sibling_count

    if message.author == client.user: last_message = message; return # Don't respond to ourselves. But, just incase we need it, also set last_message to the message.
    if not message.content: print(f"{FM.warning} Message somehow had no content. This is rather concerning. Returning."); return

    # Moderation
    # Rubicon 3 takes on the role of a silent moderator. It spies on messages and flags ones with specific keywords.
    
    message_restricted_keywords = {
        "example_rubicon_word": "!hey maybe dont do that",
        "nuh uh": "%!9|yuh huh",
    }

    for restricted_keyword in message_restricted_keywords.items():
        if restricted_keyword[0] in message.content.lower():
            # Depending on the mode in the dict..
            if restricted_keyword[1].startswith("!"):
                # We're trying to respond.
                await message.reply(restricted_keyword[1][1:], mention_author=False)
                return
            if restricted_keyword[1].startswith("%!"):
                # it has a chance to reply
                pipeindex = restricted_keyword[1].find("|")
                chance_to_reply = int(restricted_keyword[1][2:pipeindex])
                if random.randint(1, chance_to_reply) == 1:
                    await message.channel.send(restricted_keyword[1][pipeindex+1:], mention_author=False) 
                # do NOT return.

    message_has_special_character = False
    override_channel_is_all = False
    rubi_all_object = discord.utils.get(message.guild.text_channels, name=conjoined_channel_name)
    if message.content.startswith(special_character):
        # The behavior of Rubicon's response when the message starts with this character is not set in stone anymore.
        # It either blocks the message or lets it through based on a new 'mode' feature in Rubicon 3.

        # Set the flag:
        message_has_special_character = True
        # Rubicon-All checking system. Mode is forced to 1 if sent in #rubicon-all. Additionally, regardless of responding rules, the message *must* be handled, not by returning.
        if rubi_all_object and message.channel == rubi_all_object:
            override_channel_is_all = True # Never return early.
            # This is it for this entire check. The handling happens later, no matter if it has a special character or not.
        
        # Check if we're on blacklist, which is the default:
        if respond_by_default and not override_channel_is_all: # If it responds by default, which means this message is intended to be *excluded* from Rubicon.
            return
        else:
            # This is a bit different. We need to keep going, and we need to remove the character.
            message.content = message.content[1:]
    if not respond_by_default and not message_has_special_character and not override_channel_is_all:
        # A further continuation of the special character logic.
        # This message doesn't have the special character and we don't respond by default. Return.
        return
    
    # Check if guild is null - This should generally be impossible, but perhaps we're in a group chat?
    guild_available = False
    if message.guild:
        guild_available = True
    else:
        print(f"{FM.warning} Message somehow had no guild. Not a fatal error. Rubicon will continue to complain, however. This means roles are not available.")
    
    if guild_available:
        # Check if the user has a 'No Rubicon' role. This role is meant to make Rubicon ignore that user.
        no_rubicon_role_object = discord.utils.get(message.guild.roles, name=no_rubicon_role)
        if no_rubicon_role_object: # If the server has the given role.
            if no_rubicon_role_object in message.author.roles: # If the user has the given role.
                return # Return. This user is blacklisted from Rubicon.
        else:
            print(f"{FM.warning} Server '{message.guild.name}' ({message.guild.id}) has no 'No Rubicon' role. Please add one immediately.")
    
        if not respond_in_all_channels:
            # We need to check if we are not to respond in any channel.
            # And further, we also need to check if the special character is included.
            # The special character, when the mode is whitelist responses, will bypass this check.
            check_bypass = False
            if message_has_special_character and not respond_by_default:
                # Bypass this check.
                check_bypass = True
            rubi_general_object = discord.utils.get(message.guild.text_channels, name=target_channel_name)
            #rubi_all_object     = discord.utils.get(message.guild.text_channels, name=conjoined_channel_name)
            if rubi_general_object and message.channel != rubi_general_object and not check_bypass:
                if rubi_all_object and message.channel != rubi_all_object:
                    return
                elif not rubi_all_object:
                    return
            elif not rubi_general_object:
                print(f"{FM.warning} Server '{message.guild.name}' ({message.guild.id}) has no '{target_channel_name}' channel.")
                return

    msgcontent1 = await utils.user_id_fuzzymatching(message.content, client)
    msgcontent2 = msgcontent1
    if not msgcontent1:
        msgcontent1 = message.content
        msgcontent2 = msgcontent1
    if guild_available:
        msgcontent2 = await utils.role_id_fuzzymatching(msgcontent1, message.guild)
        if not msgcontent2:
            msgcontent2 = msgcontent1
    msgcontent = msgcontent2

    # Attachment handling.
    if message.attachments:
        for attachment in message.attachments:
            msgcontent += f"\n{attachment.url}"

    print(f"{FM.light_blue}{message.author.display_name} ({message.author.name}, {message.author.id}, {FM.light_yellow if rubi_all_object and message.channel == rubi_all_object else ""}{message.channel}{FM.light_blue if rubi_all_object and message.channel == rubi_all_object else ""}, {message.guild.name if guild_available else "Unknown Server"}):\n{msgcontent}")

    # Now or never.
    # Right now, right here, is where we need to figure out if we're going to early-return or not.
    # Based on Rubicon-all. God, I hate this implementation.
    if rubi_all_object and message.channel == rubi_all_object:
        await rubicon_all_handling(message.author.display_name, message.content, message.guild.name)
        # Mode forced 1. Rubicon shouldn't respond if special character not present.
        if not message_has_special_character:
            return
    try:
        response = utils.prompt_ai(msgcontent, message.author, message.channel, conversation, True, current_model, temperature, top_p, maximum_tokens,
                                   ["</s>", "[Inst]"], groq_api_key, True if message.guild else False)
        print(f"{FM.light_yellow}Rubicon:\n{response}")
        conversation.append({"role": "assistant", "content": response})
    except groq.RateLimitError as e:
        if not aggressive_error_handling:
            response = "Encountered a rate limit error. Try waiting a bit. If the issue still isn't resolved, save memory, restart Rubicon, load memory, and try again."
            print(f"{FM.warning} Rate limit error.\n'{FM.red}{e}{FM.light_yellow}'")
        else:
            response = "Encountered a rate limit error. Aggressive error handling is enabled, so Rubicon has attempted to clear it's memory to save itself. Try again in a few moments."
            print(f"{FM.warning} Rate limit error.\n'{FM.red}{e}{FM.light_yellow}'\nAggressive error handling is enabled.")
            conversation = deepcopy(restore_point)
            if increment_siblings_on_die: sibling_count += 1
            fix_conversation(old_sibling_count, sibling_count)
            write_siblings()
    except groq.GroqError as e:
        if not aggressive_error_handling:
            response = "Encountered an AI service error. Try waiting a bit. If the issue still isn't resolved, save memory, restart Rubicon, load memory, and try again."
            print(f"{FM.warning} Generic Groq error.\n'{FM.red}{e}{FM.light_yellow}'")
        else:
            response = "Encountered an AI service error. Aggressive error handling is enabled, so Rubicon has attempted to clear it's memory to save itself. Try again in a few moments."
            print(f"{FM.warning} Generic Groq error.\n'{FM.red}{e}{FM.light_yellow}'\nAggressive error handling is enabled.")
            conversation = deepcopy(restore_point)
            if increment_siblings_on_die: sibling_count += 1
            fix_conversation(old_sibling_count, sibling_count)
            write_siblings()
    except Exception as e:
        print(f"{FM.warning} AI crash.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        if not aggressive_error_handling: 
            response = "Encountered an unknown error within the AI response. Try saving the memory, restarting Rubicon, and loading it again."
        else:
            response = "Encountered an unknown error within the AI response. Aggressive error handling is enabled, so Rubicon has attempted to clear it's memory to save itself. \
Try again in a few moments."
            conversation = deepcopy(restore_point)
            if increment_siblings_on_die: sibling_count += 1
            fix_conversation(old_sibling_count, sibling_count)
            write_siblings()
    if not send_message_everywhere:
        await message.channel.send(response)
    else:
        # Send it to every rubicon-general of every single guild we're in.
        for current_guild in client.guilds:
            # Same code from the rubicon-general identification...
            rubi_general_object = discord.utils.get(current_guild.text_channels, name=target_channel_name)
            if rubi_general_object:
                # If #rubicon-general exists.
                await rubi_general_object.send(response)
            elif not rubi_general_object:
                print(f"{FM.warning} Server '{message.guild.name}' ({message.guild.id}) has no '{target_channel_name}' channel. (Not sending a response there.)")
    if override_channel_is_all:
        await rubicon_all_handling(client.user.display_name, response, message.guild.name)
# Discord (General)

def get_guilds_id_from_file() -> list[int]:
    """Returns all of the ID's within the guilds.txt file as a list."""
    try:
        with open(os.path.join(file_dirname, "guilds.txt"), "r") as guilds_file:
            lines = guilds_file.readlines()
            ids = []
            for line in lines:
                line = line.strip().split()
                ids.append(int(line[0]))
    except ValueError:
        FM.header_error("Invalid guilds.txt file format", "The file format within the guilds.txt file is invalid. Please check that the ID's are all integers.")
        sys.exit(1)
    except FileNotFoundError:
        FM.header_error("Missing critical file: guilds.txt", "The file responsible for authorizing guilds (guilds.txt) is missing.\nDid you move it, forget to create it,\
or accidentally delete it?")
        sys.exit(1)
    return ids

def get_user_ids_from_elevated_file() -> list[int]:
    """Returns all of the ID's within the rubicon_elevated.txt file as a list."""
    # Extremely similar code to get_guilds_id_from_file().
    try:
        with open(os.path.join(file_dirname, "rubicon_elevated.txt"), "r") as elevated_file:
            lines = elevated_file.readlines()
            ids = []
            for line in lines:
                line = line.strip().split()
                ids.append(int(line[0]))
    except ValueError:
        FM.header_error("Invalid rubicon_elevated.txt file format", "The file format within the rubicon_elevated.txt file is invalid. Please check that the ID's are all integers.")
        sys.exit(1)
    except FileNotFoundError:
        FM.header_error("Missing critical file: rubicon_elevated.txt", "The file responsible for authorizing elevated users (rubicon_elevated.txt) is missing.\nDid you move it,\
forget to create it, or accidentally delete it?")
        sys.exit(1)
    return ids

def get_user_ids_from_control_file() -> list[int]:
    """Returns all of the ID's within the rubicon_control.txt file as a list."""
    try:
        with open(os.path.join(file_dirname, "rubicon_control.txt"), "r") as control_file:
            lines = control_file.readlines()
            ids = []
            for line in lines:
                line = line.strip().split()
                ids.append(int(line[0]))
    except ValueError:
        FM.header_error("Invalid rubicon_control.txt file format", "The file format within the rubicon_control.txt file is invalid. Please check that the ID's are all integers.")
        sys.exit(1)
    except FileNotFoundError:
        FM.header_error("Missing critical file: rubicon_control.txt", "The file responsible for authorizing control users (rubicon_control.txt) is missing.\nDid you move it,\
forget to create it, or accidentally delete it?")
        sys.exit(1)
    return ids

async def leave_all_unauthorized_guilds(current_guilds: list[discord.Guild]) -> None:
    """Leaves all unauthorized guilds."""
    print(f"{FM.trying} Checking guilds...")
    authorized_id = get_guilds_id_from_file()
    for guild in current_guilds:
        if guild.id not in authorized_id:
            print(f"{FM.info} Found and left unauthorized guild '{guild.name}' ({guild.id}).")
            await client.get_guild(guild.id).leave()
        else:
            print(f"{FM.ginfo} Found authorized guild '{guild.name}' ({guild.id}).")

def guilds_with_rubicongeneral() -> list[discord.Guild]:
    """Returns all guilds with a channel named 'Rubicon General' (rubicon-general)."""
    return [guild for guild in client.guilds if target_channel_name in [channel.name for channel in guild.text_channels]]

def guilds_with_rubiconall() -> list[discord.Guild]:
    """Returns all guilds with a channel named 'Rubicon All' (rubicon-all)."""
    return [guild for guild in client.guilds if conjoined_channel_name in [channel.name for channel in guild.text_channels]]

def guilds_with_rubiconsystem() -> list[discord.Guild]:
    """Returns all guilds with a channel named 'Rubicon System Messages' (rubicon-system-messages)."""
    return [guild for guild in client.guilds if "rubicon-system-messages" in [channel.name for channel in guild.text_channels]]

def roles_check(user: discord.User, guild: discord.Guild | None = None, roles: list[str] = [], mode: int = 1, null_guild_allowed: bool = True) -> bool:
    """Returns whether or not the specified user has the proper roles, or if the roles do not exist.
    
    Args:
        user (discord.User): The user to check.
        guild (discord.Guild): The guild with the roles specified.
        roles (list[str]): The names of the roles to check.
        mode (int): The mode. If 0, user must have all specified roles, if 1, user must have at least one specified role. If 2, user must not have any specified roles.
        null_guild_allowed (bool): Whether or not the null guild is allowed. If True, if guild isn't found, just return 1."""
    
    if null_guild_allowed:
        if not guild:
            # Fall back to rubicon_lockdown rules.
            if rubicon_elevated_role in roles:
                if user.id in get_user_ids_from_elevated_file():
                    if mode == 2: return 0
                    if mode == 1: return 1
                else:
                    if mode == 0: return 0 # User does not meet one or more roles
            
            if rubicon_control_role in roles:
                if user.id in get_user_ids_from_control_file():
                    if mode == 2: return 0
                    if mode == 1: return 1
                else:
                    if mode == 0: return 0 # User does not meet one or more roles
            raise Exception("Somehow didn't match ANY lockdown match cases. The only way this should be possible is if provided roles list is empty.")

    if rubicon_lockdown:
        # Don't check if theres any roles. Simply check in "rubicon_elevated.txt" and "rubicon_control.txt".
        # However, do check the mode, and the roles specified.

        if rubicon_elevated_role in roles:
            if user.id in get_user_ids_from_elevated_file():
                if mode == 2: return 0
                if mode == 1: return 1
            else:
                if mode == 0: return 0 # User does not meet one or more roles
        
        if rubicon_control_role in roles:
            if user.id in get_user_ids_from_control_file():
                if mode == 2: return 0
                if mode == 1: return 1
            else:
                if mode == 0: return 0 # User does not meet one or more roles
        raise Exception("Somehow didn't match ANY lockdown match cases. The only way this should be possible is if provided roles list is empty.")
    
    user_roles = [role.id for role in user.roles]
    for role in roles:
        guild_role = discord.utils.get(guild.roles, name=role)
        if not guild_role: return 0 # Role does not exist
        if guild_role.id not in user_roles:
            if mode == 0:
                return 0 # User does not meet one or more roles
        if guild_role.id in user_roles:
            if mode == 2:
                return 0 # User has blacklisted role
            return 1
    # User does not meet at least one role for mode 1. All other modes would have returned already.
    return 0
            
async def rubicon_all_handling(username: str, message: str, guildname: str):
    """Handles all Rubicon-all related things."""
    for guild in guilds_with_rubiconall():
        if guild.name == guildname:
            continue # The message was sent here. Do not send it to the same guild.
        rubi_all_object = discord.utils.get(guild.text_channels, name=conjoined_channel_name) # Always exists, because guilds_with_rubiconall() ensures it exists.
        totalmessage = f"`({guildname})` **{username}**:\n{message}"
        if len(totalmessage) > 2000:
            totalmessage = totalmessage[0:2000-1] # -1 because 0 indexed
        await rubi_all_object.send(totalmessage)

# Discord (App Commands)
@tree.command(name="save_memory", description="Save's Rubicon's memory to a file.")
async def save_memory_cmd(ctx, file_name: str):
    """Saves Rubicon's memory to a file. Not much to say here.
    
    Args:
        file_name (str): The name of the file to save to."""
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        print(f"{FM.trying} Saving memory...")
        result = save_memory(conversation, file_name, True)
        print(f"{FM.info} Result: '{result}'")
        await ctx.response.send_message(result)
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run save_memory.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="read_memory", description="Reads Rubicon's memory from a file.")
async def read_memory_cmd(ctx, file_name: str):
    global conversation
    """Reads Rubicon's memory from a file. Not much to say here.
    
    Args:
        file_name (str): The name of the file to read from."""
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        print(f"{FM.trying} Reading memory...")
        conversation = read_memory(file_name, True)
        if not type(conversation) == str:
            print(f"{FM.success} Read memory.")
            await ctx.response.send_message("Read memory.")
        else:
            print(f"{FM.info} Failed to read memory. {conversation}")
            await ctx.response.send_message(conversation)
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run read_memory.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="display_memory", description="Send the memory in individual messages.")
async def display_memory_cmd(ctx):
    """Sends the memory in individual messages. Not much to say here."""
    await ctx.response.send_message("Displaying memory.")
    for message in conversation[1:]: # System prompt not included. We do a little bit of secrets :trollface:
        await ctx.channel.send(f"Role: `{message['role']}`, Content:")
        await ctx.channel.send(f"```{message['content']}```")
    await ctx.channel.send("Sent all messages in memory!")

@tree.command(name="force_sync", description="Forces Rubicon to sync commands to specified/all servers it is in.")
async def force_sync_cmd(ctx):
    """Forces Rubicon to sync commands to specified/all servers it is in."""
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        print(f"{FM.trying} Syncing on demand...")
        await ctx.response.send_message("Syncing on demand...")
        if not sync_commands_to_all_servers:
            await tree.sync(guild=server_to_sync_to)
        else:
            await tree.sync()
        print(f"{FM.success} Synced on demand.")
        await ctx.channel.send("Synced.")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run force_sync.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="toggle_responding", description="Toggles whether or not Rubicon responds to messages.")
async def toggle_send(ctx, state: bool | None = None):
    """Toggles whether or not Rubicon responds to messages. If state is not specified, it will toggle."""
    global respond_by_default
    if state is not None:
        respond_by_default = state
    else:
        respond_by_default = not respond_by_default
    print(f"{FM.info} Responding: {respond_by_default}")
    await ctx.response.send_message(f"Responding: {'Yes' if respond_by_default else 'No'}")

@tree.command(name="toggle_responding_all", description="Toggles whether or not Rubicon responds to messages in every channel.")
async def toggle_send_all(ctx, state: bool | None = None):
    """Toggles whether or not Rubicon responds to messages in every channel. If state is not specified, it will toggle."""
    global respond_in_all_channels
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        if state is not None:
            respond_in_all_channels = state
        else:
            respond_in_all_channels = not respond_in_all_channels
        print(f"{FM.info} Responding in all channels: {respond_in_all_channels}")
        await ctx.response.send_message(f"Responding in all channels: {'Yes' if respond_in_all_channels else 'No'}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run toggle_responding_all.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_siblings", description="Sets the amount of siblings that Rubicon has.")
async def set_siblings(ctx, amount: int):
    """Sets the amount of siblings that Rubicon has."""
    global sibling_count, old_sibling_count
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        fix_conversation(sibling_count, amount)
        old_sibling_count = sibling_count; sibling_count = amount
        write_siblings()
        print(f"{FM.info} Sibling count: {sibling_count}, old count: {old_sibling_count}")
        await ctx.response.send_message(f"Sibling count: {sibling_count}, old count: {old_sibling_count}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_siblings.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="increment_siblings", description="Increments the amount of siblings that Rubicon has.")
async def increment_siblings(ctx):
    """Increments the amount of siblings that Rubicon has."""
    global sibling_count, old_sibling_count
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        fix_conversation(sibling_count, sibling_count + 1)
        old_sibling_count = sibling_count; sibling_count += 1
        write_siblings()
        print(f"{FM.info} Sibling count: {sibling_count}, old count: {old_sibling_count}")
        await ctx.response.send_message(f"Sibling count: {sibling_count}, old count: {old_sibling_count}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run increment_siblings.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="decrement_siblings", description="Decrements the amount of siblings that Rubicon has.")
async def decrement_siblings(ctx):
    """Decrements the amount of siblings that Rubicon has."""
    global sibling_count, old_sibling_count
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        fix_conversation(sibling_count, sibling_count - 1)
        old_sibling_count = sibling_count; sibling_count -= 1
        write_siblings()
        print(f"{FM.info} Sibling count: {sibling_count}, old count: {old_sibling_count}")
        await ctx.response.send_message(f"Sibling count: {sibling_count}, old count: {old_sibling_count}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run decrement_siblings.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="reset_memory", description="Resets the memory of Rubicon. Also fixes it to the correct sibling count just in case.")
async def reset_memory(ctx):
    """Resets the memory of Rubicon. Also fixes it to the correct sibling count just in case."""
    global conversation, restore_point
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        conversation = deepcopy(restore_point)
        fix_conversation(sibling_count, sibling_count)
        print(f"{FM.info} Memory reset.")
        await ctx.response.send_message("Memory reset.")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run reset_memory.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="system_reset", description="Resets Rubicon's system prompt *only*. Allows you to update the prompt whilst running.")
async def system_reset(ctx):
    """Resets Rubicon's system prompt *only* to the base prompt. Allows you to update the prompt whilst running."""
    global conversation, restore_point
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        conversation[0] = read_memory(os.path.join(file_dirname, 'base.json'), protect_path=False)[0]
        restore_point = [deepcopy(conversation[0])]
        fix_conversation(sibling_count, sibling_count)
        print(f"{FM.info} System prompt reset.")
        await ctx.response.send_message("System prompt reset.")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run system_reset.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="display_system", description="Displays the current system prompt.")
async def display_system(ctx):
    """Displays the current system prompt."""
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role], 0):
        print(f"{FM.info} Displaying system prompt.")
        await ctx.response.send_message(f"Role: {conversation[0]["role"]}")
        await ctx.channel.send(f"Content:\n{conversation[0]["content"]}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run display_system.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_channel", description="Set the channel that Rubicon uses if restricted to one channel.")
async def set_channel_cmd(ctx, channel_name: str):
    """Set the channel that Rubicon uses if restricted to one channel."""
    global target_channel_name # Don't ask, I don't have an answer. Python dumbassary.
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        print(f"{FM.info} Setting channel to {channel_name}.")
        await ctx.response.send_message(f"Setting response channel to {channel_name}.")
        target_channel_name = channel_name
        await ctx.channel.send(f"Set channel.")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_channel.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_everywhere", description="Set everywhere toggle.")
async def set_everywhere_cmd(ctx, state: bool | None = None):
    """Set everywhere toggle."""
    global send_message_everywhere
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        if state is not None:
             send_message_everywhere = state
        else:
             send_message_everywhere = not send_message_everywhere 
        print(f"{FM.info} Responding in all channels: {send_message_everywhere}")
        await ctx.response.send_message(f"Responding in all channels: {'Yes' if send_message_everywhere else 'No'}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_everywhere.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_temperature", description="Set the temperature of Rubicon's AI.")
async def set_temperature_cmd(ctx, new_temperature: float = 0.2):
    """Set the temperature of Rubicon's AI."""
    global temperature
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        old_temp = temperature
        print(f"{FM.info} Setting temperature to {new_temperature} (previously {old_temp}).")
        temperature = new_temperature
        await ctx.response.send_message(f"Set temperature to {new_temperature} (previously {old_temp}).")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_temperature.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_model", description="Set the model Rubicon uses. (Dangerous.)")
async def set_model_cmd(ctx, new_model: str = "llama3-70b-8192"):
    global current_model
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        old_model = current_model
        if new_model not in ai_models:
            FM.header_warn("Model not found", "The model specified as the default model for Rubicon is not found. Defaulting to 'llama3-70b-8192'.")
            current_model = "llama3-70b-8192" # Default model.
            ctx.response.send_message("Model not found. Defaulting to 'llama3-70b-8192'.")
            return
        print(f"{FM.info} Setting model to {new_model} (previously {old_model}).")
        current_model = new_model
        await ctx.response.send_message(f"Set model to {new_model} (previously {old_model}).")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_model.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_max_tokens", description="Set the maximum number of tokens Rubicon can remember.")
async def set_max_tokens_cmd(ctx, new_max_tokens: int = 8192):
    """Set the maximum number of tokens Rubicon can remember."""
    global maximum_tokens
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        old_max_tokens = maximum_tokens
        print(f"{FM.info} Setting maximum tokens to {new_max_tokens} (previously {old_max_tokens}).")
        maximum_tokens = new_max_tokens
        await ctx.response.send_message(f"Set maximum tokens to {new_max_tokens} (previously {old_max_tokens}).")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_max_tokens.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_top_p", description="Set top_p. Recommended to change temperature instead.")
async def set_top_p_cmd(ctx, new_top_p: float = 1.0):
    """Set top_p. Recommended to change temperature instead."""
    global top_p
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        old_top_p = top_p
        print(f"{FM.info} Setting top_p to {new_top_p} (previously {old_top_p}).")
        top_p = new_top_p
        await ctx.response.send_message(f"Set top_p to {new_top_p} (previously {old_top_p}).")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_top_p.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="display_siblings", description="Display the number of siblings.")
async def display_siblings_cmd(ctx):
    """Display the number of siblings."""
    print(f"{FM.info} Current siblings: {sibling_count}")
    await ctx.response.send_message(f"Current siblings: {sibling_count}.")

@tree.command(name="display_old_siblings", description="Display the last number of siblings. Internal use.")
async def display_old_siblings_cmd(ctx):
    """Display the last number of siblings. Internal use."""
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        print(f"{FM.info} Last siblings: {sibling_count}")
        await ctx.response.send_message(f"Last siblings: {sibling_count}.")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run display_old_siblings.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_special_character", description="Set the special character that you start a message off with.")
async def set_special_character_cmd(ctx, new_special_character: str = "^"):
    """Set the special character that you start a message off with."""
    global special_character
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        old_special_character = special_character
        print(f"{FM.info} Setting special character to {new_special_character} (previously {old_special_character}).")
        special_character = new_special_character
        await ctx.response.send_message(f"Set special character to {new_special_character} (previously {old_special_character}).")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_special_character.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="set_rand_msg_chance", description="Set the chance for a random message. Default: 1/50.")
async def set_rand_msg_chance_cmd(ctx, new_rand_msg_chance: int = 50):
    """Set the chance for a random message. Default: 1/50."""
    global random_message_chance
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        old_rand_msg_chance = random_message_chance
        print(f"{FM.info} Setting random message chance to {new_rand_msg_chance} (previously {old_rand_msg_chance}).")
        random_message_chance = new_rand_msg_chance
        await ctx.response.send_message(f"Set random message chance to {new_rand_msg_chance} (previously {old_rand_msg_chance}).")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run set_rand_msg_chance.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")
    
@tree.command(name="add_sib_on_crash", description="Toggle adding a sibling when Rubicon crashes.")
async def add_sib_on_crash_cmd(ctx, state: bool | None = None):
    """Toggle adding a sibling when Rubicon crashes."""
    global increment_siblings_on_die
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        if state is not None:
            increment_siblings_on_die = state
        else:
            increment_siblings_on_die = not increment_siblings_on_die
        print(f"{FM.info} Increment siblings on die: {increment_siblings_on_die}")
        await ctx.response.send_message(f"Increment siblings on die: {increment_siblings_on_die}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run add_sib_on_crash.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="aggressive_errors", description="Toggle aggressive error handling, which clears memory when Rubicon crashes.")
async def aggressive_errors_cmd(ctx, state: bool | None = None):
    """Toggle aggressive error handling, which clears memory when Rubicon crashes."""
    global aggressive_error_handling
    guild = ctx.guild or None
    if roles_check(ctx.user, guild, [rubicon_control_role, rubicon_elevated_role]):
        if state is not None:
            aggressive_error_handling = state
        else:
            aggressive_error_handling = not aggressive_error_handling
        print(f"{FM.info} Aggressive error handling: {aggressive_error_handling}")
        await ctx.response.send_message(f"Aggressive error handling: {aggressive_error_handling}")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run aggressive_errors.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

# Discord (App Commands (Control))
@tree.command(name="initialize_roles_channels", description="Adds roles and channels to a specified server if it doesn't have them.", guild=client.get_guild(1234052712950136923))
async def initialize_roles_channels(ctx, guild_id: str):
    """Adds roles and channels to a specified server if it doesn't have them."""
    if not guild_id.isdigit():
        print(f"{FM.info} Invalid guild ID (initialize_roles_channels, {guild_id}).")
        await ctx.response.send_message("Invalid guild ID.")
        return

    if roles_check(ctx.user, ctx.guild, [rubicon_control_role]):
        print(f"{FM.info} Initializing roles and channels.")
        await ctx.response.send_message("Initializing roles and channels.")
        # Get the guild.
        target_guild = client.get_guild(int(guild_id))
        # Add the channels rubicon-general and rubicon-system-messages.
        if not discord.utils.get(target_guild.text_channels, name="rubicon-general"): await target_guild.create_text_channel("rubicon-general", reason="Rubi Init: rubicon-general is where Rubicon chats with people!")
        if not discord.utils.get(target_guild.text_channels, name="rubicon-system-messages"): await target_guild.create_text_channel("rubicon-system-messages", reason="Rubi Init: Rubicon is changing the server to function at maximum!")
        # Add the roles Rubicon Boot Ping, Rubicon Announcements, Rubicon Control, Rubicon Elevated, and No Rubicon.
        if not discord.utils.get(target_guild.roles, name="Rubicon Boot Ping"): await target_guild.create_role(name="Rubicon Boot Ping", color=0x9e42e0, reason="Rubi Init: Rubicon is changing the server to function at maximum!")
        if not discord.utils.get(target_guild.roles, name="Rubicon Announcements"): await target_guild.create_role(name="Rubicon Announcements", color=0x99ccff, reason="Rubi Init: Rubicon is changing the server to function at maximum!")
        if not discord.utils.get(target_guild.roles, name="Rubicon Control"): await target_guild.create_role(name="Rubicon Control", color=0x3498db, reason="Rubi Init: Rubicon is changing the server to function at maximum!")
        if not discord.utils.get(target_guild.roles, name="Rubicon Elevated"): await target_guild.create_role(name="Rubicon Elevated", color=0xe67e22, reason="Rubi Init: Rubicon is changing the server to function at maximum!")
        if not discord.utils.get(target_guild.roles, name="No Rubicon"): await target_guild.create_role(name="No Rubicon", color=0xe74c3c, reason="Rubi Init: Rubicon is changing the server to function at maximum!")
        print(f"{FM.info} Roles and channels initialized.")
        await ctx.channel.send("Roles and channels initialized.")
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run initialize_roles_channels.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

@tree.command(name="cleanup_roles_channels", description="Removes roles and channels from a specified server if they exist.", guild=client.get_guild(1234052712950136923))
async def cleanup_roles_channels(ctx, guild_id: str, leave: bool = True):
    """Removes roles and channels from a specified server if they exist."""
    if not guild_id.isdigit():
        print(f"{FM.info} Invalid guild ID (initialize_roles_channels, {guild_id}).")
        await ctx.response.send_message("Invalid guild ID.")
        return
    if roles_check(ctx.user, ctx.guild, [rubicon_control_role]):
        print(f"{FM.info} Cleaning up roles and channels.")
        await ctx.response.send_message("Cleaning up roles and channels.")
        # Get the guild.
        target_guild = client.get_guild(guild_id)
        # Remove the channels rubicon-general and rubicon-system-messages.
        discord.utils.get(target_guild.text_channels, name="rubicon-general").delete(reason="Rubicon is leaving now!")
        discord.utils.get(target_guild.text_channels, name="rubicon-system-messages").delete(reason="Rubicon is leaving now!")
        # Remove the roles Rubicon Boot Ping, Rubicon Announcements, Rubicon Control, Rubicon Elevated, and No Rubicon.
        discord.utils.get(target_guild.roles, name="Rubicon Boot Ping").delete(reason="Rubicon is leaving now!")
        discord.utils.get(target_guild.roles, name="Rubicon Announcements").delete(reason="Rubicon is leaving now!")
        discord.utils.get(target_guild.roles, name="Rubicon Control").delete(reason="Rubicon is leaving now!")
        discord.utils.get(target_guild.roles, name="Rubicon Elevated").delete(reason="Rubicon is leaving now!")
        discord.utils.get(target_guild.roles, name="No Rubicon").delete(reason="Rubicon is leaving now!")
        if leave:
            await target_guild.leave()
    else:
        print(f"{FM.info} User {ctx.user.display_name} ({ctx.user.id}) does not have high enough permissions to run cleanup_roles_channels.")
        await ctx.response.send_message(f"{ctx.user.display_name}, you do not have high enough permissions to run this command.")

###  Extras.  ###
client.run(token=discord_token)