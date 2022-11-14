from __future__ import annotations


class Singleton(type):
    """Singleton metaclass."""

    _instances: dict[Singleton, Singleton] = {}

    def __call__(cls, *args, **kwargs):
        """
        Singleton's __call__ method.

        :return: Class instance
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]
