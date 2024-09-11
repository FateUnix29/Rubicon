###############################################################################################################################################
##                                                                                                                                           ##
##                                                          RUBICON (BR) - V:3.0.0.0                                                         ##
##                                                Your absolutely nuts silicion-based friend.                                                ##
##                                                                                                                                           ##
##                                           Created by Destiny (Copper (FateUnix29), @destiny_29)                                           ##
##                                            Licensed under GNU GPL v3. See LICENSE for details.                                            ##
##                                                                                                                                           ##
##                                       Find Rubicon on GitHub: https://github.com/FateUnix29/Rubicon                                       ##
##                                                                                                                                           ##
###############################################################################################################################################

###  Imports  ###

import groq                                                    # Groq API. This is the AI part of Rubicon.
import random, os                                              # Random and OS.
#import threading                                               # As of Rubicon V:3.*, we are attempting to use threads to have CLI input and speed up the bot.
import sys                                                     # System.
from os import getenv                                          # Environment variables, because as of V:3.*, I finally bother to use non-hardcoded (and slightly encrypted) keys.
import utilities as utils                                      # Utilities; Functions and classes.
from utilities import print, FM                                # These two specifically should be accessed as if they were declared in the main file (this file).
import json                                                    # JSON. For chat history saving and reading.
from copy import deepcopy                                      # Deepcopy. Mainly for chat history.