import functools

from loguru import logger

from illuminate.common.project_logging import LOGO
from illuminate.common.project_logging import LOGO_COLOR


def show_logo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logo = f"<fg {LOGO_COLOR}>{LOGO}</fg {LOGO_COLOR}>"
        logger.opt(colors=True).success(logo)
        func(*args, **kwargs)
    return wrapper
