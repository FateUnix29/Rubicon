#-------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                     #
#                                         RUBICON LIBRARY FILE - resources/other/assembler.py                                         #
#                                 Responsible for assembling the user message into a Rubicon format.                                  #
#                                                                                                                                     #
#-------------------------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                   Imports: External Libraries                                                   ###
#-------------------------------------------------------------------------------------------------------------------------------------#

import discord                                    # Discord API        || The Discord API, implemented in Python.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                      Imports: Source Files                                                      ###
#-------------------------------------------------------------------------------------------------------------------------------------#

from resources.other.datedata import *            # Date Data          || Timestamps and time information.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                            Functions                                                            ###
#-------------------------------------------------------------------------------------------------------------------------------------#

def assemble_user_message(message: discord.Message, content_override: str | None = None) -> str:
    """Assembles the user message into a Rubicon format.
    
    :param message: The message to assemble.
    :type message: discord.Message
    :param content_override: The text that will override the message contents. Defaults to None. If none, it uses message.content
    :type content_override: str | None
    
    :return: The assembled message.
    :rtype: str"""

    message_contents = f"{message.author.display_name} ({message.author.name}, #{message.channel.name}, {message.guild.name} @ {get_datetime_accurate()}): {content_override if content_override is not None else message.content}"
    return message_contents