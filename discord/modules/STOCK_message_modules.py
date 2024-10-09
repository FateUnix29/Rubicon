from interconnections import *


@rubicon_msghook(1)
def check_same_user(local):
    msg = local['message']
    usr = msg.author
    if usr == client.user:
        local['should_return'] = True

@rubicon_msghook(1)
def check_bot(local):
    msg = local['message']
    if msg.author.bot and not msg.content.startswith(special_character):
        local['should_return'] = True