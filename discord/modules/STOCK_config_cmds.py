from interconnections import *
import jsonc, traceback
from os.path import join as pjoin

class ConfigParamError(RubiconError):
    """Raised during config read/writing."""
    def __init__(self, *objects: object) -> None:
        super().__init__(*objects)

# A little treat for some who don't like the config file.

def write_to_specified_parameter(parameter: str, value: any):
    """Try and find the parameter in the config file, and write the new value to that parameter.
    
    :param parameter: The name of the parameter to write to.
    :type parameter: str
    :param value: The value to write to the parameter.
    :type value: Any
    
    :raise ConfigParamError: The parameter does not exist in the config file.
    
    :return: None
    :rtype: None"""

    try:
        with open(pjoin(file_directory, "config.jsonc"), "r+") as cfile:
            config = jsonc.load(cfile)
            if parameter in config:
                config[parameter] = value
            else:
                raise ConfigParamError(f"Parameter {parameter} not found in config file.")
            cfile.seek(0)
            cfile.truncate()
            jsonc.dump(config, cfile, indent=4)
        logger.info(f"StockConfigCmds::write_to_specified_parameter || Successfully wrote {parameter} (= {value}) to config file. Refreshing...")
        # Refresh configurations
        read_config_file()
        get_configuration()
        logger.info("StockConfigCmds::write_to_specified_parameter || Successfully refreshed configurations.")
    except FileNotFoundError:
        logger.error("StockConfigCmds::write_to_specified_parameter || Unable to find config file. Creating file...")
        try:
            with open(pjoin(file_directory, "config.jsonc"), "w") as cfile:
                jsonc.dump({parameter: value}, cfile, indent=4)
        except PermissionError:
            logger.error("StockConfigCmds::write_to_specified_parameter || Unable to write to config file. Permissions error.")
        logger.exception("StockConfigCmds::write_to_specified_parameter || Without the config file, the program will be useless. Crashing.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"StockConfigCmds::write_to_specified_parameter || Error in config file writing: {type(e).__name__}: {e}\n{traceback.format_exc()}\n"
                     "As much as this error seems unrecoverable, it is, and we shall continue running as theoretically the write to the config file was reverted.")



@tree.command(name="change_bot_name", description=f"Change the name {bot_name} percieves itself as.")
async def change_bot_name_CMD(ctx: discord.Interaction, name: str = "Rubicon"):
    try:
        write_to_specified_parameter("bot_name", name)
        logger.info(f"StockConfigCmds::change_bot_name || Changed bot name to {name}.")
        await ctx.response.send_message(f"Changed {bot_name} to {name}.")
    except ConfigParamError:
        await ctx.response.send_message(f"Parameter {name} not found in config file.")


@tree.command(name="man_refresh", description="Manually refresh the configuration file, loading any changed values.")
async def man_refresh_CMD(ctx: discord.Interaction):
    await ctx.response.send_message("Refreshing...")
    try:
        logger.info("StockConfigCmds::man_refresh || Refreshing configurations...")
        read_config_file()
        get_configuration()
        logger.info("StockConfigCmds::man_refresh || Refreshed configurations.")
    except Exception as e:
        logger.error(f"StockConfigCmds::man_refresh || Error in config file reading: {type(e).__name__}: {e}\n{traceback.format_exc()}\n"
                     "As much as this error seems unrecoverable, it is, and we shall continue running as theoretically the read from the config file was reverted.")
        await ctx.channel.send("Refresh failed.")
    await ctx.channel.send("Refreshed configurations.")


@tree.command(name="set_special_char", description="Set the special character for the bot to use.")
async def set_special_char_CMD(ctx: discord.Interaction, char: str = "^"):
    try:
        write_to_specified_parameter("special_char", char)
        logger.info(f"StockConfigCmds::set_special_char || Changed special char to {char}.")
        await ctx.response.send_message(f"Changed special char to {char}.")
    except ConfigParamError:
        await ctx.response.send_message(f"Parameter {char} not found in config file.")