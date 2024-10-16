from interconnections import *

@rubicon_fncall
def request_documentation(_, name: str) -> str:
    """Request documentation for a *function call* module. Try using it on this one!
    
    :param name: The name of the module.
    :type name: str
    :return: The documentation for the module.
    :rtype: str
    """

    if name in modules_fncall:
        return modules_fncall[name][0].__doc__ or "This module has no documentation."
    else:
        return f"Documentation for {name} not found."