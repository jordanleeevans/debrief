from enum import StrEnum


class Maps(StrEnum):
    SCAR = "SCAR"
    RAID = "RAID"
    EXPOSURE = "EXPOSURE"
    DEN = "DEN"
    COLOSSUS = "COLOSSUS"
    BLACKHEART = "BLACKHEART"


class GameModes(StrEnum):
    HARDPOINT = "HARDPOINT"
    SEARCH_AND_DESTROY = "SEARCH AND DESTROY"
    OVERLOAD = "OVERLOAD"


class Teams(StrEnum):
    GUILD = "TEAM GUILD"
    JSOC = "JSOC"
