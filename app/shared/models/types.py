from typing import Union, Annotated
from pydantic import Field
from app.shared.models.enums import AssaultRifles, SubMachineGuns, SniperRifles, Pistols

Knife = str  # There are too many melee weapons to enumerate, so we will just use a string for the knife type.

PrimaryWeaponType = Annotated[
    AssaultRifles | SubMachineGuns | SniperRifles,
    Field(description="Primary weapon type, must be one of the defined enums"),
]

SecondaryWeaponType = Annotated[
    Pistols,
    Field(description="Secondary weapon type, must be one of the defined enums"),
]
