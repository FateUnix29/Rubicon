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

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                          Initialization                                                         ###
#-------------------------------------------------------------------------------------------------------------------------------------#

# None...

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                            Functions                                                            ###
#-------------------------------------------------------------------------------------------------------------------------------------#

def ai_prompt(
        conversation: list[dict[str, str]],
        model: str,
        temp: float,
        top_p: float,
        max_tokens: int,
        restricted_phrases: list[str],
        groq_key: str,
) -> str:
    """Prompts Rubicon. Basically just an alias.

    :param conversation: The conversation history.
    :param model: The name of the model to use.
    :param temp: The temperature to use.
    :param top_p: The top_p to use.
    :param max_tokens: The maximum tokens to use."""

    # We are not modifying the conversation. We are entirely expecting the rest of the code to do that, this time.

    groq_instance = groq.Groq(api_key=groq_key)

    ai_completion = groq_instance.chat.completions.create(
        model=model,
        messages=conversation,
        temperature=temp,
        top_p=top_p,
        max_tokens=max_tokens,
    )

    ai_response = ""
    for chunk in ai_completion:
        ai_response += chunk.choices[0].delta.content or ""
    for phrase in restricted_phrases:
        ai_response = ai_response.replace(phrase, "")
    if ai_response.strip() == "":
        print(f"{FM.info} No response from Rubicon.")
        ai_response = "No response."
    return ai_response[:1999], ai_response