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


class AssaultRifles(StrEnum):
    M15_MOD_0 = "M15 MOD 0"
    PEACEKEEPER_MK1 = "PEACEKEEPER MK1"


class SubMachineGuns(StrEnum):
    DRAVEC_45 = "DRAVEC 45"


class SniperRifles(StrEnum):
    VS_RECON = "VS RECON"


class Pistols(StrEnum):
    JAEGER_45 = "JÄGER 45"
    CODA_9 = "CODA 9"
