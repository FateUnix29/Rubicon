from interconnections import *

@rubicon_readyhook(stage=1)
def welcome_message(_):
    """Print a welcome message."""
    width = 100 # Columns
    print(f"{FM.yellow}#{'-' * (width-2)}#")
    print(f"{FM.yellow}#{' ' * (width-2)}#")
    rubicon_tag = f"RUBICON ({version})"
    rubicon_spacing_left = ((width-2) - len(rubicon_tag)) // 2
    rubicon_spacing_right = rubicon_spacing_left + 1 if rubicon_spacing_left % 2 == 0 else rubicon_spacing_left
    print(f"{FM.yellow}# {' ' * (rubicon_spacing_left-1)}{rubicon_tag}{' ' * (rubicon_spacing_right-1)} #")
    rubicon_tag2 = "'Your friendly, nuts Discord bot, and ingame companion.'"
    rubicon_spacing_left2 = ((width-2) - len(rubicon_tag2)) // 2
    rubicon_spacing_right2 = rubicon_spacing_left2 + 1 if rubicon_spacing_left2 % 2 == 0 else rubicon_spacing_left2
    print(f"{FM.yellow}# {' ' * (rubicon_spacing_left2-1)}{rubicon_tag2}{' ' * (rubicon_spacing_right2-1)} #")
    print(f"{FM.yellow}#{' ' * (width-2)}#")
    print(f"{FM.yellow}#{'-' * (width-2)}#")

    logger.info("Hello World, from the modules system!")

@rubicon_readyhook()
async def boot_msg_and_ping_people(_):
    if notify_on_boot:
        guilds_without_rubicongen = list(client.guilds)

        for guild_with_rubicongen in get_guilds_with_channel_name(home_channel_name):
            logger.info(f"Found guild with '#{home_channel_name}': {guild_with_rubicongen.name} with ID {guild_with_rubicongen.id}.")
            guilds_without_rubicongen.remove(guild_with_rubicongen)
            # We iterate through the guilds with the rubicon general channel instead of system messages, just incase system messages is not found.
            target_boot_channel = discord.utils.get(guild_with_rubicongen.text_channels, name="rubicon-system-messages")

            if not target_boot_channel:
                # Change to general. General will always exist, else we wouldn't be iterating through this list.
                target_boot_channel = discord.utils.get(guild_with_rubicongen.text_channels, name="rubicon-general")

            embed = discord.Embed(
                title="Rubicon Online!",
                description="Rubicon has come online. Feel free to talk and whatnot!",
                color=discord.Color.green()
            )

            role = discord.utils.get(guild_with_rubicongen.roles, name=role_rubiboot)
            
            if role:
                role = f"<@&{role.id}>"
            if dev_mode:
                role = "Rubicon is in development mode, no ping."
            if not role:
                logger.warning(f"Guild '{guild_with_rubicongen.name}' with ID {guild_with_rubicongen.id} has no role named '{role_rubiboot}'.")
                role = f"No boot role found... ('{role_rubiboot}')"
            
            await target_boot_channel.send(role, embed=embed)
    else:
        logger.info("Not notifying people of boot.")