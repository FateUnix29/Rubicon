from interconnections import *


@rubicon_msghook(1)
def check_same_user(local):
    msg = local['message']
    usr = msg.author
    if usr == client.user:
        local['should_return'] = True