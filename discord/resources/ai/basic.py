#-------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                     #
#                                             RUBICON LIBRARY FILE - resources/ai/basic.py                                            #
#                                                The most primary functions of the AI.                                                #
#                                                                                                                                     #
#-------------------------------------------------------------------------------------------------------------------------------------#


#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                   Imports: External Libraries                                                   ###
#-------------------------------------------------------------------------------------------------------------------------------------#

import groq                                       # Groq               || The Groq library. Used as the AI brains.
import os                                         # OS                 || Functions for interacting with the OS. Mostly used for pathing.
import random                                     # Random             || Random number generation.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                      Imports: Source Files                                                      ###
#-------------------------------------------------------------------------------------------------------------------------------------#

from resources.other.colors import *              # ANSI Color Coding  || Terminal color coding.
from interconnections import logger               # Logging            || Used for logging. This is dangerously close to a circular import,
                                                                        # But interconnections will never need this file, so it's fine.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                          Initialization                                                         ###
#-------------------------------------------------------------------------------------------------------------------------------------#

groq_instance = None

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                            Functions                                                            ###
#-------------------------------------------------------------------------------------------------------------------------------------#

def init_groq(key: str) -> None:
    """Initialize the Groq instance."""
    global groq_instance
    groq_instance = groq.Groq(api_key=key)

def ai_prompt(
        conversation: list[dict[str, str]],
        model: str,
        temp: float,
        top_p: float,
        max_tokens: int,
        restricted_phrases: list[str],
) -> str:
    """Prompts Rubicon. Basically just an alias.

    :param conversation: The conversation history.
    :type conversation: list[dict[str, str]]
    :param model: The name of the model to use.
    :type model: str
    :param temp: The temperature to use.
    :type temp: float
    :param top_p: The top_p to use.
    :type top_p: float
    :param max_tokens: The maximum tokens to use.
    :type max_tokens: int
    :param restricted_phrases: The list of restricted phrases. These are removed from the response.
    :type restricted_phrases: list[str]
    
    :return: The response from Rubicon.
    :rtype: str
    """

    # We are not modifying the conversation. We are entirely expecting the rest of the code to do that, this time.

    ai_completion = groq_instance.chat.completions.create(
        model=model,
        messages=conversation,
        temperature=temp,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=True
    )

    ai_response = ""
    for chunk in ai_completion:
        ai_response += chunk.choices[0].delta.content or ""
    for phrase in restricted_phrases:
        ai_response = ai_response.replace(phrase, "")
    if ai_response.strip() == "":
        print(f"{FM.info} No response from Rubicon...")
        logger.info("We got no response from Rubicon.")
    return ai_response[:1999], ai_response