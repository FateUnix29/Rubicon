# This module is extremely important. It limits the guilds your bot can enter.
# If the guilds file is not present, by default, it will allow all guilds.
# If it is present, then any guild not listed within it will be left. This includes when joining a guild.

# If it is not present, and your bot gets onto a server controlled by a bad actor, then they could add the roles to themselves and take over the bot.
# Do not let this happen. The guilds file is heavily recommended.

# File name: guilds.txt
# Line format: (guild id, no spaces or parentheses)
# The guildfile reader doesn't care about anything after the first space. It's recommended to use a format similar to this:
# (ID, no parentheses or spaces) (name in parantheses, ignored as it is after the first space)
# That way you can keep track.

from interconnections import *
import traceback

def read_guilds_file():
    path = pjoin(file_directory, "guilds.txt")
    if not exists(path):
        return None # Code for allowing all guilds.

    try:
        with open(path, "r") as file:
            return [int(guild_id.split()[0].strip()) for guild_id in file.readlines()]

    except Exception as e:
        FM.header_error("Fatal Exception: Unable to read guilds file",
        f"Guilds file was present, but reading of it failed.\n{type(e).__name__}: {e}\n{traceback.format_exc()}")
        logger.critical(f"StockGuildVerif::read_guilds_file || Guilds file was present but failed to read. This is extremely dangerous; Fix immediately.\n{traceback.format_exc()}")
        return None # Just return the default.. Don't wanna leave all guilds.

@mark_generic_event()
@client.event
async def on_guild_join(guild: discord.Guild):
    returned_locals = locals()
    should_return = False

    for module in list(get_modules_of_parameters("on_guild_join").values()):
        if module[-1]:
            val = await module[0](locals()) # -1: Is a coro?

        else:
            val = module[0](locals())

        returned_locals.update(val if isinstance(val, dict) and val else {})
        should_return = returned_locals.get('should_return', False)
        if should_return: return

@rubicon_generichook("on_guild_join")
async def verify_guild_join(locals_):
    guilds = read_guilds_file()

    if guilds is None:
        logger.info("StockGuildVerif::verify_guild_join || Something happened to the guildfile. Defaulting to allowing all guilds.")
        return

    guild: discord.Guild = locals_["guild"]

    if guild.id not in guilds:
        embed = discord.Embed(title="Unauthorized join activity", description="This guild was *not* whitelisted.\nSorry, but I'm leaving now.\n"
                              f"If this was a mistake, contact {bot_name}'s owner.", color=discord.Color.red())
        await guild.text_channels[0].send(embed=embed)
        await guild.leave()
        print(f"{FM.warning} StockGuildVerif::verify_guild_join || Unauthorized join activity. Leaving guild '{guild.name}' (with ID {guild.id}).")
        logger.info(f"StockGuildVerif::verify_guild_join || Unauthorized join activity. Leaving guild '{guild.name}' (with ID {guild.id}).")

@rubicon_readyhook(2)
async def verify_all_guilds(_):
    guilds = read_guilds_file()

    if guilds is None:
        logger.info("StockGuildVerif::verify_all_guilds || Something happened to the guildfile. Defaulting to allowing all guilds.")
        return
    
    for guild in client.guilds:
        if guild.id not in guilds:
            embed = discord.Embed(title="Unauthorized join activity", description="This guild was *not* whitelisted.\nSorry, but I'm leaving now.\n"
                                  f"If this was a mistake, contact {bot_name}'s owner.", color=discord.Color.red())
            await guild.text_channels[0].send(embed=embed)
            await guild.leave()
            print(f"{FM.warning} StockGuildVerif::verify_all_guilds || Unauthorized join activity. Leaving guild '{guild.name}' (with ID {guild.id}).")
            logger.info(f"StockGuildVerif::verify_all_guilds || Unauthorized join activity. Leaving guild '{guild.name}' (with ID {guild.id}).")
        else:
            print(f"{FM.ginfo} StockGuildVerif::verify_all_guilds || Found valid guild '{guild.name}' (with ID {guild.id}).")
            logger.info(f"StockGuildVerif::verify_all_guilds || Found valid guild '{guild.name}' (with ID {guild.id}).")

