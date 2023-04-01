from __future__ import annotations

import functools
from pydoc import locate
from timeit import default_timer
from typing import Callable, TYPE_CHECKING

from loguru import logger

from illuminate.common import LOGO
from illuminate.common import LOGO_COLOR

if TYPE_CHECKING:
    from illuminate.manager import Manager


def show_info(func: Callable) -> Callable:
    """
    Displays ETL process information.

    :param func: Manager's public method
    :return: Manager's public method wrapper
    """

    @functools.wraps(func)
    def wrapper(self: Manager) -> None:
        """
        Displays ETL process information.

        :param self: Manager object
        :return: None
        """
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

    def log_context(self: Manager) -> None:
        """
        Displays ETL context information.

        :param self: Manager object
        :return: None
        """
        logger.opt(colors=True).info(
            f"Project files for project "
            f"<yellow>{self.name}</yellow> loaded into context"
        )
        logger.info(f"Adapters discovered {[i for i in self.adapters]}")
        logger.info(
            f"Models discovered {[locate(i) for i in self.settings.MODELS]}"
        )
        logger.info(f"Observers discovered {[i for i in self.observers]}")

    def log_results(self: Manager) -> None:
        """
        Displays ETL results information.

        :param self: Manager object
        :return: None
        """
        logger.success("Results gathered")
        logger.opt(colors=True).info(
            f"<yellow>Unsuccessful</yellow> observations: "
            f"<magenta>{len(self.not_observed)}</magenta>"
        )
        logger.debug(f"Unsuccessful attempts {self.not_observed}")
        logger.opt(colors=True).info(
            f"<yellow>Successful</yellow> observations: "
            f"<magenta>{len(self.observed) - len(self.not_observed)}</magenta>"
        )
        logger.opt(colors=True).info(
            f"Number of <yellow>exports</yellow>: "
            f"<magenta>{len(self.exported)}</magenta>"
        )

    def log_settings(self: Manager) -> None:
        """
        Displays ETL settings information.

        :param self: Manager object
        :return: None
        """
        settings_conn = self.settings.CONCURRENCY
        settings_db = self.settings.DB.copy()
        for db in settings_db:
            settings_db[db]["pass"] = "****"  # nosec
        settings_obs = self.settings.OBSERVATION_CONFIGURATION.copy()
        settings_obs["http"]["auth_password"] = "****"  # nosec
        logger.debug(f"Concurrency settings {settings_conn}")
        logger.debug(f"Database settings {settings_db}")
        logger.debug(f"Observation settings {settings_obs}")

    return wrapper


def show_logo(func: Callable) -> Callable:
    """
    Displays framework's logo.

    :param func: Manager's public method
    :return: Manager's public method wrapper
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        """
        Displays framework's logo.

        :return: None
        """
        logo = f"<fg {LOGO_COLOR}>{LOGO}</fg {LOGO_COLOR}>"
        logger.opt(colors=True).success(logo)
        func(*args, **kwargs)

    return wrapper


def show_observer_catalogue(func: Callable) -> Callable:
    """
    Displays Observers found in project files.

    :param func: CLI's function
    :return: CLI's function wrapper
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        """
        Displays Observers found in project files.

        :return: None
        """
        context = func(*args, **kwargs)
        if not context["observers"]:
            logger.info("No observers found")
        outputs = []
        for observer in context["observers"]:
            _observer = observer()
            _io = _observer.initial_observations
            outputs.append(
                f"<yellow>{_observer.__class__}</yellow> -> "
                f"<cyan>{[(i.url, i._callback.__name__)for i in _io]}</cyan>"
            )
        for output in outputs:
            logger.opt(colors=True).info(output)

    return wrapper
