import functools
from pydoc import locate
from timeit import default_timer

from loguru import logger

from illuminate.common.project_logging import LOGO
from illuminate.common.project_logging import LOGO_COLOR


def show_info(func):
    @functools.wraps(func)
    def wrapper(self):
        logger.info("Process started")
        start = default_timer()
        log_context(self)
        log_settings(self)
        func(self)
        end = default_timer() - start
        log_results(self)
        logger.opt(colors=True).info(
            f"Process finished in <yellow>{end:.2f}</yellow> seconds"
        )

    def log_context(self):
        logger.opt(colors=True).info(
            f"Project files for project "
            f"<yellow>{self.name}</yellow> loaded into context"
        )
        logger.info(f"Adapters discovered {[i for i in self.adapters]}")
        logger.info(
            f"Models discovered {[locate(i) for i in self.settings.MODELS]}"
        )
        logger.info(f"Observers discovered {[i for i in self.observers]}")

    def log_results(self):
        logger.success("Results gathered")
        logger.opt(colors=True).info(
            f"<yellow>Unsuccessful</yellow> observations: "
            f"<magenta>{len(self.failed)}</magenta>"
        )
        logger.debug(f"Unsuccessful attempts {self.failed}")
        logger.opt(colors=True).info(
            f"<yellow>Successful</yellow> observations: "
            f"<magenta>{len(self.requested) - len(self.failed)}</magenta>"
        )
        logger.opt(colors=True).info(
            f"Number of <yellow>exports</yellow>: "
            f"<magenta>{len(self.exported)}</magenta>"
        )

    def log_settings(self):
        settings_conn = self.settings.CONCURRENCY
        settings_db = self.settings.DB.copy()
        settings_db["password"] = "****"
        settings_obs = self.settings.OBSERVER_CONFIGURATION
        logger.debug(f"Concurrency settings {settings_conn}")
        logger.debug(f"Database settings {settings_db}")
        logger.debug(f"Observer settings {settings_obs}")

    return wrapper


def show_logo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logo = f"<fg {LOGO_COLOR}>{LOGO}</fg {LOGO_COLOR}>"
        logger.opt(colors=True).success(logo)
        func(*args, **kwargs)

    return wrapper
