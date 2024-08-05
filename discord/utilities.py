from builtins import print as print_ins

import discord
import groq

class FM:
    reset = '\x1b[0m\x1b[49m'
    red, blue, green, yellow, purple, cyan, white, black, \
    light_blue, light_green, light_red, light_purple, light_white, light_black, \
    light_cyan, light_yellow, bold, underline, italic, reverse, strikethrough, \
    remove_color, remove_bold, remove_underline, remove_italic, remove_reverse, \
    remove_strikethrough, bg_red, bg_green, bg_blue, bg_yellow, bg_black, \
    bg_white, bg_light_red, bg_light_green, bg_light_blue, bg_light_yellow, \
    bg_light_black, bg_light_white, bg_purple, bg_light_purple, bg_cyan, bg_light_cyan = (
        '\x1b[31m', '\x1b[34m', '\x1b[32m', '\x1b[33m', '\x1b[35m', '\x1b[36m', '\x1b[37m', '\x1b[30m', '\x1b[94m', '\x1b[92m', '\x1b[91m', '\x1b[95m', '\x1b[97m',
        '\x1b[90m', '\x1b[96m', '\x1b[93m', '\x1b[1m', '\x1b[4m', '\x1b[3m', '\x1b[7m', '\x1b[9m', '\x1b[39m', '\x1b[22m', '\x1b[24m', '\x1b[23m', '\x1b[27m', '\x1b[29m',
        '\x1b[41m', '\x1b[42m', '\x1b[44m', '\x1b[43m', '\x1b[40m', '\x1b[47m', '\x1b[101m', '\x1b[102m', '\x1b[104m', '\x1b[103m', '\x1b[100m', '\x1b[107m', '\x1b[45m',
        '\x1b[105m', '\x1b[46m', '\x1b[106m'
    )
    info, success, error, warning, debug, test = (f'{reverse}{light_blue}[INFO]{remove_reverse}', f'{reverse}{light_green}[SUCCESS]{remove_reverse}', f'{reverse}{light_red}[ERROR]',
    f'{reverse}{light_yellow}[WARNING]{remove_reverse}', f'{reverse}{light_purple}[DEBUG]{remove_reverse}', f'{reverse}{light_cyan}[TEST]{remove_reverse}')

    infod1, infod2, infod3 = (f'{reverse}{light_blue}[INFO] (L1){remove_reverse}', f'{reverse}{light_blue}[INFO] (L2){remove_reverse}', f'{reverse}{light_blue}[INFO] (L3){remove_reverse}')
    warningd1, warningd2, warningd3 = (f'{reverse}{light_yellow}[WARNING] (L1){remove_reverse}', f'{reverse}{light_yellow}[WARNING] (L2){remove_reverse}', f'{reverse}{light_yellow}[WARNING] (L3){remove_reverse}')
    debugd1, debugd2, debugd3 = (f'{reverse}{light_purple}[DEBUG] (L1){remove_reverse}', f'{reverse}{light_purple}[DEBUG] (L2){remove_reverse}', f'{reverse}{light_purple}[DEBUG] (L3){remove_reverse}')

    trying = f"{reverse}{light_yellow}[TRYING]{remove_reverse}"
    ginfo = f"{reverse}{light_green}[INFO]{remove_reverse}"

    @staticmethod
    def header_warn(header, msg):
        print(f"{FM.warning} {header}{FM.remove_reverse}\n{msg}")
    @staticmethod
    def header_error(header, msg):
        print(f"{FM.error} {header}{FM.remove_reverse}\n{msg}")
    """    @staticmethod
    def header_info(header, msg):
        print(f"{FM.info} {header}{FM.remove_reverse}\n{msg}")
    @staticmethod
    def header_success(header, msg):
        print(f"{FM.success} {header}\n{msg}")"""

def print(*args, end='\n', reset_color=True, **kwargs):
    if reset_color: print_ins(*args, end=f"{end}{FM.reset}", **kwargs)
    else: print_ins(*args, end=f"{end}", **kwargs)

# (large) Discord-related functions

# (large) Other general functions
def prompt_ai(message_contents: str, author: str, channel: discord.TextChannel | discord.VoiceChannel, conversation: list[dict[str, str]],
              use_conversation: bool, model: str, temp: float, top_p: float, max_tokens: int, restricted_phrases: list[str], groq_key: str) -> str:
    """Prompts Rubicon's AI processing and returns the response given.

    Args:
        message_contents (str): The contents of the message to be processed.
        author (str): The name of the author of the message.
        channel (discord.TextChannel | discord.VoiceChannel): The channel the message was sent in.
        conversation (list[dict[str, str]]): The conversation history.
        use_conversation (bool): Whether or not to use the conversation history. If not, you are expected to add it to the history yourself.
        model (str): The name of the model to use.
        temp (float): The temperature to use.
        top_p (float): The top_p to use.
        max_tokens (int): The maximum tokens to use.
        restricted_phrases (list[str]): The list of restricted phrases. These are removed from the response.
        groq_key (str): The GroqCloud API key. For obvious security reasons, this should not be shared and a good way to protect it is to put it in an environment variable."""
    # Assemble the message.
    if use_conversation:
        message = f"{author} (in '#{channel.name}', '{channel.guild.name}'): {message_contents}"
        conversation.append({"role": "user", "content": message})
    # Create our Groq instance
    groq_instance = groq.Groq(api_key=groq_key)
    # Create a completion
    ai_completion = groq_instance.chat.completions.create(
        model=model,
        messages=conversation,
        temperature=temp,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=True,
        stop=None
    )
    # Process the response
    ai_response = ""
    for chunk in ai_completion:
        ai_response += chunk.choices[0].delta.content or ""
    for phrase in restricted_phrases:
        ai_response = ai_response.replace(phrase, "")
    if ai_response.strip() == "":
        print(f"{FM.info} No response from Rubicon.")
        ai_response = "No response."
    # Truncate messages to 2000 characters max
    ai_response = ai_response[:1999]
    return ai_response