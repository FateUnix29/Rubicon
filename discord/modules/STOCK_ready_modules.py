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