from interconnections import *
from copy import deepcopy

@tree.command(name="load_memory", description="Load memory from file.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def load_memory_CMD(ctx: discord.interactions.Interaction, file_name: str | None = None):
    """Load memory from file."""
    global conversation

    if not file_name: file_name = "memory.json"
    file_name = os.path.basename(file_name.strip()) # If the user is going to try funny stuff, it's just going to ignore them lol

    # No extension?
    if not os.path.splitext(file_name)[1]: file_name = f"{file_name}.json"

    path = pjoin(file_directory, "memories", file_name)

    try:
        with open(path, "r") as file:
            memory = json.load(file)
            conversation = deepcopy([])
            conversation = deepcopy(memory)
            await ctx.response.send_message(f"Loaded memory from `{file_name}`.")
            logger.info(f"StockMemoryHandler::load_memory || Loaded memory from '{file_name}'.")
            return

    except FileNotFoundError:
        await ctx.response.send_message(f"File `{file_name}` not found.")
        logger.error(f"StockMemoryHandler::load_memory || File '{file_name}' not found.")
        return

    except Exception as e:
        await ctx.response.send_message(f"Failed to load memory from `{file_name}`.\n{type(e).__name__}: {e}")
        logger.error(f"StockMemoryHandler::load_memory || Failed to load memory from '{file_name}'.\n{type(e).__name__}: {e}")
        return
    

@tree.command(name="save_memory", description="Save memory to file.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def save_memory_CMD(ctx: discord.interactions.Interaction, file_name: str | None = None):
    """Save memory to file."""

    if not file_name: file_name = "memory.json"
    file_name = os.path.basename(file_name.strip()) # If the user is going to try funny stuff, it's just going to ignore them lol

    # No extension?
    if not os.path.splitext(file_name)[1]: file_name = f"{file_name}.json"

    path = pjoin(file_directory, "memories", file_name)

    try:
        with open(path, "w") as file:
            json.dump(conversation, file, indent=4)
            await ctx.response.send_message(f"Saved memory to `{file_name}`.")
            logger.info(f"StockMemoryHandler::save_memory || Saved memory to '{file_name}'.")

    except Exception as e:
        await ctx.response.send_message(f"Failed to save memory to `{file_name}`.\n{type(e).__name__}: {e}")
        logger.error(f"StockMemoryHandler::save_memory || Failed to save memory to '{file_name}'.\n{type(e).__name__}: {e}")
        return
    
@tree.command(name="display_memory", description="Display the current memory in individual messages.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def read_mem_CMD(ctx: discord.interactions.Interaction):
    """Display the current memory in individual messages."""
    global conversation # Safe than sorry.

    if not conversation:
        await ctx.response.send_message("Memory is empty.")
        logger.info("StockMemoryHandler::read_mem_CMD || Tried to display memory, but memory is empty.")
        return

    await ctx.response.send_message("CONVERSATION START")
    convo_to_log = [f"Role: `{message['role']}`, Content: ```{message['content']}```" for message in conversation]
    logger.info(f"StockMemoryHandler::read_mem_CMD || Started displaying memory, contents:\n{"\n".join(convo_to_log)}")

    for message in conversation:
        string_to_send = f"Role: `{message['role']}`, Content: ```{message['content']}```"
        
        if len(string_to_send) > 2000:
            ending_str = "``` ... Contents too large to send fully ..."
            string_to_send = f"{string_to_send[:1999-len(ending_str)]}{ending_str}"
        
        await ctx.channel.send(string_to_send)
    
    await ctx.channel.send("Done...")


@tree.command(name="reset_memory", description="Reset memory to the base prompt.")
@app_commands.checks.has_any_role(role_rubicontrol, role_rubielevated)
async def reset_memory_CMD(ctx: discord.interactions.Interaction):
    """Reset memory to the base prompt."""
    global conversation
    conversation = deepcopy(get_replace_system_prompt())
    await ctx.response.send_message("Memory reset.")