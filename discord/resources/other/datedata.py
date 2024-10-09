#-------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                     #
#                                                 RUBICON LIBRARY FILE - datedata.py                                                  #
# This file is responsible for numerous operations regarding the date and the time, most commonly getting the current date in various #
#                                                         levels of accuracy.                                                         #
#                                                                                                                                     #
#-------------------------------------------------------------------------------------------------------------------------------------#


import datetime                                   # Datetime           || Date & time interface and information.
import time                                       # Time               || Time information, time.sleep(), etc.

#-------------------------------------------------------------------------------------------------------------------------------------#
###                                                            Functions                                                            ###
#-------------------------------------------------------------------------------------------------------------------------------------#

def get_datetime_superinaccurate(separator: str = " | ") -> str:
    """Get the current date and time in a very inaccurate manner.

    :param separator: The character(s) between the date and the time.
    :type separator: str
    
    :return: The date and time.
    :rtype: str
    """

    # Inaccurate:
    #  9/26/2024 (american format) | 8 PM
    return datetime.datetime.now().strftime(f"%m/%d/%Y{separator}%H:%M %p")

def get_datetime_inaccurate(separator: str = " | ") -> str:
    """Get the current date and time in an inaccurate manner.

    :param separator: The character(s) between the date and the time.
    :type separator: str
    
    :return: The date and time.
    :rtype: str
    """

    # Inaccurate:
    #  9/26/2024 (american format) | 8:26 PM
    return datetime.datetime.now().strftime(f"%m/%d/%Y{separator}%I:%M %p")

def get_datetime(separator: str = " | ") -> str:
    """Get the current date and time in a standard manner.

    :param separator: The character(s) between the date and the time.
    :type separator: str
    
    :return: The date and time.
    :rtype: str
    """

    # Standard:
    #  9/26/2024 (american format) | 8:26:29 PM
    return datetime.datetime.now().strftime(f"%m/%d/%Y{separator}%I:%M:%S %p")

def get_datetime_accurate(separator: str = " | ") -> str:
    """Get the current date and time in an accurate manner.

    :param separator: The character(s) between the date and the time.
    :type separator: str
    
    :return: The date and time.
    :rtype: str
    """

    # Accurate:
    #  26/9/2024 (most of the world format) | 20:26:29
    return datetime.datetime.now().strftime(f"%m/%d/%Y{separator}%H:%M:%S")