from interconnections import *
import re, traceback
from copy import deepcopy

# Rubicon-all
rubicon_all_last_user = None
rubicon_all_last_guild = None

reminders_in_mem = []

# Long term memory
def try_write_longterm(remove_system_prompts: bool = True):
    baseprompt = get_replace_system_prompt()
    try:
        with open(longterm_file, 'w') as f:
            if remove_system_prompts:
                longterm = [entry for entry in longterm if entry['content'] != baseprompt[0]['content']]
            json.dump(longterm, f, indent=4)
        logger.info("StockMessageModules::try_write_longterm || Refreshed long-term memory file.")
        return 0
    except Exception as e:
        logger.error(f"StockMessageModules::try_write_longterm || Could not refresh long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return 1
    
def try_get_longterm():
    try:
        with open(longterm_file, 'r') as f:
            longterm = json.load(f)
        logger.info("StockMessageModules::try_get_longterm || Loaded long-term memory file.")
        return longterm
    except FileNotFoundError:
        logger.error("StockMessageModules::try_get_longterm || Could not load long-term memory file. File not found. Creating...")
        try:
            with open(longterm_file, 'w') as f:
                json.dump([{}], f, indent=4)
            logger.info("StockMessageModules::try_get_longterm || Created new long-term memory file.")
        except Exception as e:
            logger.error(f"StockMessageModules::try_get_longterm || Could not create new long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return [{}]
    except Exception as e:
        logger.error(f"StockMessageModules::try_get_longterm || Could not load long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return [{}]


# Heavily inspired by the MindCraft project, in fact, the code from there was ported into Python for this. Huge shoutout to them.
def word_overlap_score(text1, text2):
    words1 = text1.split()
    words2 = text2.split()
    intersection = set(words1) & set(words2)
    return len(intersection) / (len(words1) + len(words2) - len(intersection))

# This function, too, is taken from the MindCraft project.
def im_reminded_by_this(conversation):
    """Gets relevant long-term memory objects."""
    if len(longterm) == 0: return []
    turn_text = ' '.join([turn['content'] for turn in conversation])
    longterm_copy = deepcopy(longterm) # Safety. Don't screw up the original.
    # Cut out every message that is both in long term and in the current conversation.
    longterm_copy = [x for x in longterm_copy if x not in conversation]
    longterm_copy.sort(key=lambda x: word_overlap_score(turn_text, x['content']), reverse=True)
    selected = longterm_copy[:2]

    for selected_item in selected:
        if selected_item in reminders_in_mem:
            selected.remove(selected_item)

    if selected == []: return []
    
    reminders_in_mem.extend(selected)

    print(f"{FM.yinfo} Rubicon has been reminded of {len(selected)} messages:\n{"\n-----------------------------------\n".join([content["content"] for content in selected])}")
    logger.info(f"StockMessageModules::im_reminded_by_this || Reminded Rubicon of {len(selected)} messages: {selected}")

    return deepcopy(selected) # deep copy

longterm_file = os.path.join(file_directory, "memories", "longterm.json")
longterm = try_get_longterm()

@rubicon_msghook(1)
def save_message_to_longterm(locals_):
    msg: discord.Message = locals_['message']
    if msg.content:
        longterm.append({'role': f"{'user' if msg.author != client.user else 'assistant'}", 'content': msg.content})
        try_write_longterm()

@rubicon_msghook(1)
def ensure_we_are_in_a_guild(locals_):
    msg: discord.Message = locals_['message']
    if not msg.guild:
        logger.info("StockMessageModules::ensure_we_are_in_a_guild || Message was not in a guild, returning.")
        locals_['should_return'] = True

@rubicon_msghook(1)
def check_if_no_content(locals_):
    if not locals_['message'].content:
        logger.info(f"Recieved a message from {locals_['message'].author.display_name} ({locals_['message'].author.id}) that had no content.")
        locals_['should_return'] = True # No attachment handling yet.

@rubicon_msghook(1)
def check_same_user(locals_):
    msg: discord.Message = locals_['message']
    usr = msg.author
    if usr == client.user and not msg.channel.name == all_channel_name: # Completely ignore rubicon-all, it wont feedback loop.
        locals_['should_return'] = True

@rubicon_msghook(1)
def check_bot(locals_):
    msg: discord.Message = locals_['message']
    if msg.author.bot and not msg.content.startswith(special_character):
        locals_['should_return'] = True

@rubicon_msghook(1)
async def verify_special_character_usage(locals_):
    global rubicon_all_last_user, rubicon_all_last_guild # WHY must PYTHON SHADOW THESE FUCKING GLOBALS I SWEAR TO GOD
    msg: str = locals_['message_contents']
    msg_raw: discord.Message = locals_['message']

    # Modes:
    # If in mode 0, and message starts with special char OR not in rubicon's general channel, skip.
    # If in mode 1, and message doesn't start with special char, skip.
    # If in conjoined channel, force mode 1

    message_has_special_character = msg.startswith(special_character)
    skip_general_check = False
    in_all_channel = False
    locals_["message_has_special_character"] = message_has_special_character
    locals_["skip_general_check"] = skip_general_check
    locals_["in_all_channel"] = in_all_channel

    tmp_mode = respond_by_default

    print(f"{message_has_special_character=}\n{tmp_mode=}\n{skip_general_check=}\n{in_all_channel=}\n{msg_raw.channel.name}\n{msg_raw.guild.name}")

    if msg_raw.channel.name == all_channel_name:
        print("we're in all")
        tmp_mode = True
        skip_general_check = True
        in_all_channel = True
        locals_["in_all_channel"] = in_all_channel
        locals_["skip_general_check"] = skip_general_check
    
    if not tmp_mode and not skip_general_check:
        print("if mode is 0 and general check is not skipped")
        if message_has_special_character or msg_raw.channel.name != home_channel_name:
            print("message either has special character or we're not in the general channel")
            locals_['should_return'] = True
            print(f"{locals_=}\n\n{locals_['should_return']=}")
    
    elif tmp_mode and not message_has_special_character:
        print("if mode is 1 and message does not start with special char")
        locals_['should_return'] = True

    print(locals_)

    # Before the on_message routine returns, we must handle rubicon-all, since we've now dug a hole for ourselves with a should_return flag.
    if in_all_channel and all_channel_enabled:
        guildname = msg.guild.name
        username = msg.author.display_name
        all_str = f"`({guildname})` **{username}**:{msg}" if username != rubicon_all_last_user or guildname != rubicon_all_last_guild else f"{msg}"
        for guild_w_rubiall in get_guilds_with_channel_name(all_channel_name):
            if guild_w_rubiall.name == guildname:
                continue # Don't send it back here.
            all_str = all_str[:1999] # Cut it off to the 2000 character limit, as bots don't have nitro.
            all_object = discord.utils.get(guild_w_rubiall.text_channels, name=all_channel_name) # WILL exist as we're iterating over only guilds that have this channel
            await all_object.send(all_str)

        rubicon_all_last_user = msg.author.display_name
        rubicon_all_last_guild = msg.guild.name

    return locals_

def check_token_limit(msg):
    # Count words and special characters
    word_count = len(re.findall(r'\b\w+\b', msg))
    special_char_count = len(re.findall(r'[^\w\s]', msg))
    
    # Calculate total tokens
    total_tokens = word_count + special_char_count
    return total_tokens > context_length

@rubicon_msghook(2)
def long_term_memory_handling(locals_):
    msg: str = locals_['message_contents']
    try: # I don't trust im_reminded_by_this to be reliable just yet.
        reminders = im_reminded_by_this(conversation)
    except Exception as e:
        logger.debug(f"StockMessageModules::long_term_memory_handling || Bad! Bad! Bad! I knew that thing wasn't reliable!\nError in im_reminded_by_this:\n{type(e).__name__}: {e}\n"
        f"{traceback.format_exc()}")
        reminders = []
    if reminders == []:
        msg += "(COULD NOT RETRIEVE LONG TERM MEMORY.)"
        reminders = ['[[[Failed to retrieve long term memory]]]']
    else:
        msg += "(End of user's message.)\n\n(This reminds you of something from your long term memory...)\n"
        for reminder in reminders:
            msg += f"{reminder['content']}\n"
        msg = msg.strip()

@rubicon_msghook(3)
async def user_id_fuzzymatching(locals_):
    """Uses RegEx to find and replace all pings (relating to a user) (<@user>) with their display name."""
    pattern = r"\<@\d+\>"
    matches = []

    message: str = locals_['message_contents']

    if re.search(pattern, message):
        match_iter = re.finditer(pattern, message)
        for match in match_iter:
            matches.append(match.group(0)[2:-1])
    
    if matches:
        for user_id in matches:
            try:
                username = client.get_user(int(user_id))
                if username:
                    message = message.replace(f"<@{user_id}>", f"@{username.display_name}")
                else:
                    username = await client.fetch_user(int(user_id))
                    if username:
                        message = message.replace(f"<@{user_id}>", f"@{username.display_name}")
                    else:
                        message = message.replace(f"<@{user_id}>", f"@unknown-user")
            except Exception as e:
                print(f"{FM.info} Could not find pinged user with ID {user_id}. ({type(e).__name__}: {e})\n{traceback.format_exc()}")
                logger.warning(f"StockMessageModules::user_id_fuzzymatching || Could not find pinged user with ID {user_id}. ({type(e).__name__}: {e})\n{traceback.format_exc()}")
                message = message.replace(f"<@{user_id}>", f"@unknown-user")

    #if re.match(pattern, message):
    #    return re.sub(pattern, await _try_get_user(int(message[2:-1]), client), message)

    return message

@rubicon_msghook(3)
async def role_id_fuzzymatching(locals_):
    """Uses RegEx to find and replace all pings (relating to a role) (<@&role>) with their name."""
    pattern = r"\<@\&\d+\>"
    matches = []
    
    message: str = locals_['message_contents']
    guild: discord.Guild = locals_['message'].guild

    if re.search(pattern, message):
        match_iter = re.finditer(pattern, message)
        for match in match_iter:
            matches.append(match.group(0)[3:-1])

    
    if matches:
        for role_id in matches:
            try:
                rolename = guild.get_role(int(role_id))
                if rolename:
                    message = message.replace(f"<@&{role_id}>", f"@{rolename}")
                else:
                    message = message.replace(f"<@&{role_id}>", f"@unknown-role")
            except Exception as e:
                print(f"{FM.info} Could not find pinged role with ID {role_id}. ({type(e).__name__}: {e})\n{traceback.format_exc()}")
                logger.warning(f"StockMessageModules::role_id_fuzzymatching || Could not find pinged role with ID {role_id}. ({type(e).__name__}: {e})\n{traceback.format_exc()}")
                message = message.replace(f"<@&{role_id}>", f"@unknown-role")

@rubicon_msghook(3)
def check_if_conversation_is_overlimit(locals_):
    msg = locals_['message_contents']
    if check_token_limit(msg):

        if conversation[1] in reminders_in_mem:
            # This is a reminder! Remove it.
            reminders_in_mem.remove(conversation[1])
        
        conversation = conversation[1:]