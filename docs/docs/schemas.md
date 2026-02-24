---
sidebar_position: 5
---

# Schemas & Types

All data flowing through Debrief is validated against strict Pydantic schemas. This page documents every schema, enum, and type alias used across the bot and API.

---

## Enums

### `Maps` {#maps}

Supported Call of Duty maps.

| Value |
|-------|
| `SCAR` |
| `RAID` |
| `EXPOSURE` |
| `DEN` |
| `COLOSSUS` |
| `BLACKHEART` |

### `GameModes` {#gamemodes}

Supported game modes.

| Value |
|-------|
| `HARDPOINT` |
| `SEARCH AND DESTROY` |
| `OVERLOAD` |

### `Teams` {#teams}

Team identifiers.

| Value |
|-------|
| `TEAM GUILD` |
| `JSOC` |

### `AssaultRifles` {#assaultrifles}

| Value |
|-------|
| `M15 MOD 0` |
| `PEACEKEEPER MK1` |

### `SubMachineGuns` {#submachineguns}

| Value |
|-------|
| `DRAVEC 45` |

### `SniperRifles` {#sniperrifles}

| Value |
|-------|
| `VS RECON` |

### `Pistols` {#pistols}

| Value |
|-------|
| `JÄGER 45` |
| `CODA 9` |

---

## Type Aliases

### `PrimaryWeaponType` {#primaryweapontype}

Union of [`AssaultRifles`](#assaultrifles) | [`SubMachineGuns`](#submachineguns) | [`SniperRifles`](#sniperrifles).

### `SecondaryWeaponType` {#secondaryweapontype}

Alias for [`Pistols`](#pistols).

### `Knife` {#knife}

`str` — free-text field for melee weapon names (too many variants to enumerate).

---

## Weapon Schemas

### `WeaponStats` {#weaponstats}

Base model for weapon statistics. All fields are validated with min/max constraints.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `eliminations` | `int` | 0–200 | Number of eliminations |
| `elimination_death_ratio` | `float` | 0–200.0 | Elimination to death ratio |
| `damage_dealt` | `int` | 0–10,000 | Total damage dealt |
| `headshot_kills` | `int` | 0–200 | Number of headshot kills |
| `headshot_percentage` | `float` | 0–100.0 | Percentage of headshots |
| `accuracy_percentage` | `float` | 0–100.0 | Shot accuracy percentage |

### `PrimaryWeaponStats` {#primaryweaponstats}

Extends [`WeaponStats`](#weaponstats).

| Field | Type | Description |
|-------|------|-------------|
| `primary_weapon_name` | [`PrimaryWeaponType`](#primaryweapontype) | Name of the primary weapon |

### `SecondaryWeaponStats` {#secondaryweaponstats}

Extends [`WeaponStats`](#weaponstats).

| Field | Type | Description |
|-------|------|-------------|
| `secondary_weapon_name` | [`SecondaryWeaponType`](#secondaryweapontype) | Name of the secondary weapon |

### `MeleeWeaponStats` {#meleeweaponstats}

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `melee_weapon_name` | [`Knife`](#knife) | — | Name of the melee weapon |
| `kill_death_ratio` | `float` | 0–200.0 | K/D ratio with this weapon |
| `damage_dealt` | `int` | 0–10,000 | Damage dealt with this weapon |

---

## Scoreboard Schemas

### `Scoreboard` {#scoreboard}

Base scoreboard model shared by all game modes.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `player` | `str` | — | Player's in-game name |
| `eliminations` | `int` | 0–200 | Number of eliminations |
| `deaths` | `int` | 0–200 | Number of deaths |
| `elimination_death_ratio` | `float` | 0–200.0 | Elimination to death ratio |
| `score` | `int` | ≥ 0 | Player's score |

### `HardpointScoreboard` {#hardpointscoreboard}

Extends [`Scoreboard`](#scoreboard).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `time` | `int` | ≥ 0 | Time in hardpoint (seconds) |
| `objective_captures` | `int` | ≥ 0 | Objective captures |
| `objective_kills` | `int` | ≥ 0 | Objective kills |
| `captures` | `int` | ≥ 0 | Captures |
| `friendly_score` | `int` | 0–250 | Friendly team score |
| `enemy_score` | `int` | 0–250 | Enemy team score |

### `OverloadScoreboard` {#overloadscoreboard}

Extends [`Scoreboard`](#scoreboard).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `overloads` | `int` | ≥ 0 | Overloads achieved |
| `overload_devices_carrier_killed` | `int` | ≥ 0 | Overload carriers killed |
| `friendly_score` | `int` | 0–8 | Friendly team score |
| `enemy_score` | `int` | 0–8 | Enemy team score |

### `SearchAndDestroyScoreboard` {#searchanddestroyscoreboard}

Extends [`Scoreboard`](#scoreboard).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `plants` | `int` | ≥ 0 | Bomb plants |
| `defuses` | `int` | ≥ 0 | Bomb defuses |
| `objective_kills` | `int` | ≥ 0 | Objective kills |
| `objective_score` | `int` | ≥ 0 | Objective score |
| `friendly_score` | `int` | 0–6 | Friendly team score |
| `enemy_score` | `int` | 0–6 | Enemy team score |

---

## Game Stats Schemas

### `GameStats` {#gamestats}

Base game stats model.

| Field | Type | Description |
|-------|------|-------------|
| `primary_weapon_stats` | [`PrimaryWeaponStats`](#primaryweaponstats) | Primary weapon statistics |
| `secondary_weapon_stats` | [`SecondaryWeaponStats`](#secondaryweaponstats) | Secondary weapon statistics |
| `melee_weapon_stats` | [`MeleeWeaponStats`](#meleeweaponstats) | Melee weapon statistics |
| `map` | [`Maps`](#maps) | Map played |
| `team` | [`Teams`](#teams) | Player's team |

### `GameStatsResponse` {#gamestatsresponse}

Response model used for API output and Gemini validation. Extends the base fields from [`GameStats`](#gamestats) (with weapon stats made optional) and adds:

| Field | Type | Description |
|-------|------|-------------|
| `game_mode` | [`GameModes`](#gamemodes) | Game mode played |
| `scoreboard` | [`HardpointScoreboard`](#hardpointscoreboard) \| [`OverloadScoreboard`](#overloadscoreboard) \| [`SearchAndDestroyScoreboard`](#searchanddestroyscoreboard) | Scoreboard for the game mode |

A `model_validator` ensures the scoreboard type matches the `game_mode` — e.g. a `HARDPOINT` game must have a [`HardpointScoreboard`](#hardpointscoreboard).

---

## Document Schemas

### `MatchDocument` {#matchdocument}

The schema for documents stored in MongoDB.

| Field | Type | Description |
|-------|------|-------------|
| `discord_user_id` | `int` | Discord user ID |
| `discord_message_id` | `int` | Discord message ID |
| `discord_channel_id` | `int` | Discord channel ID |
| `game_stats` | [`GameStatsResponse`](#gamestatsresponse) | Full game stats |
| `created_at` | `datetime` | Timestamp of insertion |

---

## Query Pipeline Schemas

These schemas validate AI-generated MongoDB aggregation pipelines, restricting them to a safe subset of read-only operations.

### `MongoStage` {#mongostage}

A single aggregation pipeline stage.

| Field | Type | Description |
|-------|------|-------------|
| `operator` | [`ALLOWED_AGGREGATION_OPERATORS`](#allowed_aggregation_operators) | The aggregation operator |
| `expression` | `dict \| int \| float \| str \| bool \| list` | The operator's expression |

A `model_validator` enforces that `$limit`/`$skip` expressions are numeric and `$match`/`$sort`/`$project`/`$group` expressions are objects.

### `MongoPipeline` {#mongopipeline}

| Field | Type | Description |
|-------|------|-------------|
| `stages` | `list[`[`MongoStage`](#mongostage)`]` | Ordered list of pipeline stages |

### `ALLOWED_AGGREGATION_OPERATORS` {#allowed_aggregation_operators}

A `Literal` type restricting operators to the following read-only set:

`$match` · `$group` · `$project` · `$sort` · `$limit` · `$skip` · `$unwind`
