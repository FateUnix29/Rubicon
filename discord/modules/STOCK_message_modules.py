from interconnections import *
import re, traceback
from copy import deepcopy
import shutil

# Rubicon-all
rubicon_all_last_user = None
rubicon_all_last_guild = None

reminders_in_mem = []
reminders_in_mem_2 = []
longterm = []

# Long term memory

def longterm_checksum() -> bool:
    """Check if longterm is valid."""
    verification = [x for x in longterm if 'content' in x and x['content'] != '' and 'role' in x and x['role'] != '']
    if verification != longterm:
        # PANIC. Checksum incorrect.
        # Longterm is in an **invalid state** and we cannot remember anything.
        logger.error("StockMessageModules::longterm_checksum || Long-term checksum **INCORRECT!** Longterm is in an invalid state!")
        return True
    logger.info("StockMessageModules::longterm_checksum || Long-term checksum **CORRECT!**")
    return False

def try_clone_longterm():
    try:
        if os.path.exists(longterm_file_old):
            os.remove(longterm_file_old)
        shutil.copy(longterm_file, longterm_file_old)
        logger.info("StockMessageModules::try_clone_longterm || Cloned long-term memory file.")
        return False
    except Exception as e:
        logger.error(f"StockMessageModules::try_clone_longterm || Could not clone long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return True
    return True # Failed

def try_write_longterm(remove_system_prompts: bool = True):
    global longterm
    #print(longterm)
    baseprompt = get_replace_system_prompt()
    try:
        with open(longterm_file, 'w') as f:
            if try_clone_longterm(): # Err code 1: BAD
                logger.error("StockMessageModules::try_write_longterm || Couldn't clone long-term memory file before blanking it. Aborting for safety.")
                return 1
            else:
                f.seek(0)
                f.write("") # Clear the file.
                f.seek(0)
                if remove_system_prompts and not longterm_checksum():
                    longterm = [entry for entry in longterm if 'content' in entry and entry['content'] != baseprompt[0]['content'] and entry not in reminders_in_mem]
                else:
                    logger.warning("StockMessageModules::try_write_longterm || Long-term checksum failed, somehow. Not checking for system prompts.")

                json.dump(longterm, f, indent=4)

        logger.info("StockMessageModules::try_write_longterm || Refreshed long-term memory file.")
        return 0

    except Exception as e:
        logger.error(f"StockMessageModules::try_write_longterm || Could not refresh long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return 1
    
def try_get_longterm():
    global longterm
    try:
        with open(longterm_file, 'r') as f:
            # Check if the file is empty.
            read_file = f.read()
            if read_file == "":
                logger.info("StockMessageModules::try_get_longterm || Nothing to get.")
                return []
            f.seek(0) # Return to zero.
            longterm = json.load(f)
        logger.info("StockMessageModules::try_get_longterm || Loaded long-term memory file.")
        return longterm
    except FileNotFoundError:
        logger.error("StockMessageModules::try_get_longterm || Could not load long-term memory file. File not found. Creating...")
        try:
            with open(longterm_file, 'w') as f:
                json.dump([], f, indent=4)
            logger.info("StockMessageModules::try_get_longterm || Created new long-term memory file.")
        except Exception as e:
            logger.error(f"StockMessageModules::try_get_longterm || Could not create new long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return []
    except Exception as e:
        logger.error(f"StockMessageModules::try_get_longterm || Could not load long-term memory file.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return []


# Heavily inspired by the MindCraft project, in fact, the code from there was ported into Python for this. Huge shoutout to them.
def word_overlap_score(text1: str, text2: str):
    if text2 == "": return 0
    if text1 == "": return 0
    if text1 == text2: return 1
    words1 = text1.split()
    words2 = text2.split()
    intersection = set(words1) & set(words2)
    return len(intersection) / (len(words1) + len(words2) - len(intersection))

# This function, too, is taken from the MindCraft project.
def im_reminded_by_this(conversation):
    """Gets relevant long-term memory objects."""
    if len(longterm) <= 1: return []
    if longterm_checksum(): return []

    turn_text = ' '.join([turn['content'] for turn in conversation])
    longterm_copy = deepcopy(longterm) # Safety. Don't screw up the original.
    # Cut out every message that is both in long term and in the current conversation.
    longterm_copy = [x for x in longterm_copy if x not in conversation]
    longterm_copy.sort(key=lambda x: word_overlap_score(turn_text, x['content'] if 'content' in x else ''), reverse=True)
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
longterm_file_old = os.path.join(file_directory, "memories", "longterm.json~")
longterm = try_get_longterm()

def convo_and_log():
    logger.warning("StockMessageModules::save_messages_to_longterm || Conversation didn't start with a system prompt?")
    return conversation

@rubicon_msghook(4)
def save_messages_to_longterm(_):
    conversation_wo_prompt = conversation[1:] if conversation[0]['role'] == 'system' else convo_and_log()
    conversation_wo_prompt = [message for message in conversation_wo_prompt if message not in reminders_in_mem]
    #print(f"XOR={[x for x in longterm if x not in conversation_wo_prompt]}")
    if len(conversation_wo_prompt) != 0:
        longterm.extend(conversation_wo_prompt[-2:])
        try_write_longterm()

@rubicon_msghook(1)
def ensure_we_are_in_a_guild(locals_):
    msg: discord.Message = locals_['message']
    if not msg.guild:
        logger.info("StockMessageModules::ensure_we_are_in_a_guild || Message was not in a guild, returning.")
        locals_['should_return'] = True

    return locals_

@rubicon_msghook(1)
def check_if_no_content(locals_):
    msg_raw: discord.Message = locals_['message']
    if not msg_raw.content:
        logger.info(f"Recieved a message from {msg_raw.author.display_name} ({msg_raw.author.id}) that had no content.")
        if msg_raw.attachments:
            logger.info("Do note, however, that this message had attachments. Not implemented yet.")
        locals_['should_return'] = True # No attachment handling yet.

    return locals_

@rubicon_msghook(1)
def check_same_user(locals_):
    msg: discord.Message = locals_['message']
    usr = msg.author
    if usr == client.user and not msg.channel.name == all_channel_name: # Completely ignore rubicon-all, it wont feedback loop.
        locals_['should_return'] = True

    return locals_

@rubicon_msghook(1)
def check_bot(locals_):
    msg: discord.Message = locals_['message']
    if msg.author.bot and not msg.content.startswith(special_character):
        locals_['should_return'] = True

    return locals_

@rubicon_msghook(1)
async def verify_special_character_usage(locals_):
    global rubicon_all_last_user, rubicon_all_last_guild # WHY must PYTHON SHADOW THESE GLOBALS I SWEAR TO GOD
    msg: str = locals_['message_contents']
    msg_raw: discord.Message = locals_['message']
    header: str = locals_['proto_content']

    # Modes:
    # If in mode 0, and message starts with special char OR not in rubicon's general channel, skip.
    # If in mode 1, and message doesn't start with special char, skip.
    # If in conjoined channel, force mode 1

    message_has_special_character = msg_raw.content.startswith(special_character)

    if message_has_special_character:
        # Use proto content to remove the header information, and the special character.
        msg = msg[len(header)+len(special_character):]
        # *Carefully* reassemble the message.
        msg = f"{header}{msg}"
        locals_['message_contents'] = msg.strip()

    skip_general_check = False
    in_all_channel = False
    locals_["message_has_special_character"] = message_has_special_character
    locals_["skip_general_check"] = skip_general_check
    locals_["in_all_channel"] = in_all_channel

    tmp_mode = respond_by_default

    if msg_raw.channel.name == all_channel_name: # If in rubicon's all channel
        tmp_mode = True
        skip_general_check = True
        in_all_channel = True
        locals_["in_all_channel"] = in_all_channel
        locals_["skip_general_check"] = skip_general_check

    if not tmp_mode and not skip_general_check: # If mode 0, and not in rubicon-all (if not skip general check)
        if message_has_special_character and msg_raw.channel.name in home_channel_names: # If the message has the special character and is in the home channel
            if not msg_raw.author.bot: # If not a bot. This little guy needs to step in now. A prior module has checked for this. We don't need to check again.
                locals_['should_return'] = True
        
        elif msg_raw.channel.name not in home_channel_names: # If not in the home channel
            if f"<@{client.user.id}>" not in msg_raw.content:
                locals_['should_return'] = True
            else:
                pass

    
    elif tmp_mode and not message_has_special_character: # If mode 1, and the message doesn't start with the special character
        locals_['should_return'] = True

    elif tmp_mode and message_has_special_character: # If mode 1, and the message starts with the special character
        if f"<@{client.user.id}>" not in msg_raw.content:
            locals_['should_return'] = True

    # Before the on_message routine returns, we must handle rubicon-all, since we've now dug a hole for ourselves with a should_return flag.
    if in_all_channel and all_channel_enabled:
        guildname = msg_raw.guild.name
        username = msg_raw.author.display_name
        all_str = f"`({guildname})` **{username}**: {msg_raw.content}" if username != rubicon_all_last_user or guildname != rubicon_all_last_guild else f"{msg_raw.content}"
        for guild_w_rubiall in get_guilds_with_channel_name(all_channel_name):
            if guild_w_rubiall.name == guildname:
                continue # Don't send it back here.
            all_str = all_str[:1999] # Cut it off to the 2000 character limit, as bots don't have nitro.
            all_object = discord.utils.get(guild_w_rubiall.text_channels, name=all_channel_name) # WILL exist as we're iterating over only guilds that have this channel
            await all_object.send(all_str)

        rubicon_all_last_user = username
        rubicon_all_last_guild = guildname

    return locals_

@rubicon_msghook(1)
def check_if_reply(locals_):
    msg: str = locals_['message_contents']
    header: str = locals_['proto_content']
    msg_raw: discord.Message = locals_['message']

    if msg_raw.reference:
        ref = msg_raw.reference
        ref_author = ref.resolved.author
        # We're replying to someone. Reconstruct the message.
        header_nocol = header[:-2] # Get rid of the last character. (There's also a space at the end.)
        msg = f"{header_nocol} (In response to {ref_author.display_name}): {msg[len(header):]}"
        locals_['message_contents'] = msg.strip()

    return locals_
        

def check_token_limit(msg):
    # Count words and special characters
    word_count = len(re.findall(r'\b\w+\b', msg))
    special_char_count = len(re.findall(r'[^\w\s]', msg))
    
    # Calculate total tokens
    total_tokens = word_count + special_char_count
    return total_tokens > context_length

@rubicon_msghook(2)
def long_term_memory_handling(_):
    global conversation
    msg = ""

    try: # I don't trust im_reminded_by_this to be reliable just yet.
        reminders = im_reminded_by_this(conversation)
    
    except Exception as e:
        logger.debug(f"StockMessageModules::long_term_memory_handling || Bad! Bad! Bad! I knew that thing wasn't reliable!\nError in im_reminded_by_this:\n{type(e).__name__}: {e}\n"
        f"{traceback.format_exc()}")
        reminders = []
    
    if reminders == []:
        return # Just be quiet, damn it...

    else:
        msg += "(The user's message reminds you of something from your long term memory...)\n"
        for reminder in reminders:
            msg += f"{reminder['content']}\n"
        msg = msg.strip()
    
    dict_object = {"role": "system", "content": msg}
    conversation.append(dict_object)
    dict_object2 = deepcopy(dict_object)
    dict_object2["reminders"] = reminders
    reminders_in_mem_2.append(dict_object2)

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

    return {"message_contents": message} # Once again, do not touch anything else.

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

    return {"message_contents": message}

@rubicon_msghook(4)
def check_if_conversation_is_overlimit(_):
    global conversation # Once again, this isn't even bound unless we do this. Why, Python3, why?!
    msgs = [message["content"] if "content" in message else None for message in conversation[1:]]
    msgs = list(filter(None, msgs))
    msgs = " ".join(msgs)
    while check_token_limit(msgs): # Loop until we're below the token limit.

        if conversation[1] in reminders_in_mem_2:
            # This is a reminder! Remove it.
            reminders_in_mem.remove(reminders_in_mem_2[conversation[1]["reminders"]])
            reminders_in_mem_2.remove(conversation[1])
        
        conversation = conversation[1:]