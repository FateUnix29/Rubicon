###############################################################################################################################################
##                                                                                                                                           ##
##                                                            RUBICON - V:3.0.0.0                                                            ##
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
from discord.app_commands import CommandTree                   # This allows for slash commands.
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

### Constants ###

_ver = "3.0.0.0"

###  Globals  ###
bot_name = "Rubicon"                                           # Name of the bot/AI.