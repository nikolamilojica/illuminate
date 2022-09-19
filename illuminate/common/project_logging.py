from illuminate import __version__

LOGGING_LEVELS = (
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
)

LOGO = f"""
  ___ _     _    _   _ __  __ ___ _   _    _  _____ _____
 |_ _| |   | |  | | | |  \/  |_ _| \ | |  / \|_   _| ____|
  | || |   | |  | | | | |\/| || ||  \| | / _ \ | | |  _|
  | || |___| |__| |_| | |  | || || |\  |/ ___ \| | | |___
 |___|_____|_____\___/|_|  |_|___|_| \_/_/   \_\_| |_____|

Version: {__version__}
"""  # noqa:  W291, W605

LOGO_COLOR = "239,242,201"
