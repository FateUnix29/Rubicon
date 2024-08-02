###############################################################################################################################################
##                                                                                                                                           ##
##                                                            RUBICON - V:3.0.0.4                                                            ##
##                                                Your absolutely nuts silicion-based friend.                                                ##
##                                                                                                                                           ##
##                                           Created by Destiny (Copper (FateUnix29), @destiny_29)                                           ##
##                                         Licensed under (NOT CHOSEN YET). See LICENSE for details.                                         ##
##                                                                                                                                           ##
##                                       Find Rubicon on GitHub: https://github.com/FateUnix29/Rubicon                                       ##
##                                                                                                                                           ##
###############################################################################################################################################

###  Imports  ###

import discord                                                 # Discord API.
from discord import app_commands                               # This allows for slash commands.
import groq                                                    # Groq API. This is the AI part of Rubicon.
import random, os                                              # Random and OS.
import threading                                               # As of Rubicon V:3.*, we are attempting to use threads to have CLI input and speed up the bot.
import sys                                                     # System.
from os import getenv                                          # Environment variables, because as of V:3.*, I finally bother to use non-hardcoded (and slightly encrypted) keys.
import utilities                                               # Utilities; Functions and classes.
from utilities import print, FM                                # These two specifically should be accessed as if they were declared in the main file (this file).

###   Init    ###

# For some explanation on this section, there are a few things that I'd like to do before everything else.

# Get python interpreter version
ver = sys.version_info
ver = f"{ver.major}.{ver.minor}.{ver.micro} ({ver.releaselevel})"
expected = "3.12.3 (final)"
if ver != expected:
    print(f"\n{FM.light_yellow}Small warning:\nYour Python interpreter does not match that of what Rubicon was developed with.\n\
This, of course, may cause errors. The version of your Python interpreter is {ver}, and Rubicon was developed with {expected}.\n")
    if sys.version_info.minor < 10:
        print(f"{FM.light_red}Attention: You are using Python 3.9x or lower. This *will* cause errors which will likely stop Rubicon in it's tracks.")

### Constants ###

_ver = "3.0.0.4"

###  Globals  ###

# Basic variables
bot_name = "Rubicon"                                     # Name of the bot/AI.
last_message = None                                      # Incase we need it.

# AI-specific variables
current_model = "llama3-70b-8192"                        # Name of the current model. Heavily influences AI behavior.
temperature = 0.2                                        # Model temperature. Temperature is a number that influences how likely it is to choose less-likely words.
top_p = 1                                                # Top-p. Not too sure what this does, so no description. Change this or temperature, but probably not both.
maximum_tokens = 8192                                    # Maximum context length. This is the maximum number of tokens the AI can remember. Default is 8192, the max for llama3-70b-8192.
last_ai_message = None                                   # I absolutely doubt that we'll need this, but it's here.
random_message_chance = 50                               # The chance that a random message will be sent in addition to the AI's response. Default is 50 (1 in 50).

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
send_message_everywhere = True                           # Does Rubicon send it's response across all servers, giving the look of it seeing things that don't exist?

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
# Discord (Event Handlers)

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

def leave_all_unauthorized_guilds(current_guilds: list[discord.Guild]) -> None:
    """Leaves all unauthorized guilds."""
    print(f"{FM.trying}Checking guilds...")
    authorized_id = get_guilds_id_from_file()
    for guild in current_guilds:
        if guild.id not in authorized_id:
            print(f"{FM.info}Found and left unauthorized guild '{guild.name}' ({guild.id}).")
            client.get_guild(guild.id).leave()
        else:
            print(f"{FM.ginfo}Found authorized guild '{guild.name}' ({guild.id}).")
            

# Discord (App Commands)

# Discord (App Commands (Control))

