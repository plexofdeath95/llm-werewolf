"""All Werewolf roles. Every module in this package registers its roles on import."""
import importlib
import pkgutil

from aiplays.modes.werewolf.roles.base import ROLES

for _m in pkgutil.iter_modules(__path__):
    if _m.name not in ("base", "effects", "effects_info", "traps"):
        importlib.import_module(f"{__name__}.{_m.name}")

__all__ = ["ROLES"]
