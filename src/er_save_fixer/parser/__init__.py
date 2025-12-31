"""ER Save Fixer Parser package."""

from .character import PlayerGameData, SPEffect
from .equipment import EquippedItems, EquippedSpells, Inventory
from .er_types import FloatVector3, FloatVector4, HorseState, MapId
from .save import Save, load_save
from .user_data_10 import Profile, ProfileSummary, UserData10
from .user_data_x import UserDataX
from .world import (
    FaceData,
    PlayerCoordinates,
    RideGameData,
    WorldAreaTime,
    WorldAreaWeather,
)

__all__ = [
    # Main classes
    "Save",
    "load_save",
    "UserDataX",
    "UserData10",
    "Profile",
    "ProfileSummary",
    # Character data
    "PlayerGameData",
    "SPEffect",
    # Equipment
    "Inventory",
    "EquippedSpells",
    "EquippedItems",
    # World data
    "RideGameData",
    "WorldAreaWeather",
    "WorldAreaTime",
    "PlayerCoordinates",
    "FaceData",
    # Types
    "MapId",
    "HorseState",
    "FloatVector3",
    "FloatVector4",
]

# Keep in sync with `pyproject.toml` and `version_info.txt` (PyInstaller).
__version__ = "3.2.0"

"""ER Save Fixer package."""

__all__ = ["__version__"]

# Keep this in sync with `version_info.txt` (PyInstaller) and `pyproject.toml`.
__version__ = "3.2.0"

"""ER Save Fixer package."""

__all__ = ["__version__"]

# Keep this in sync with PyInstaller's `version_info.txt` as needed.
__version__ = "3.2.0"
