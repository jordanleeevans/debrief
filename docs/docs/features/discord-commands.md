---
sidebar_position: 1
---

# Discord Commands

Debrief provides three Discord commands for interacting with the bot.

## `!ping`

Health check command to verify the bot is online.

**Usage:**
```
!ping
```

**Response:** `Pong!`

---

## `!stats`

Extract game statistics from Call of Duty screenshots using Gemini AI.

**Usage:**
1. Type `!stats` in a Discord channel
2. Attach 1–2 screenshot images (each under 10 MB)

**What happens:**
1. The bot downloads the attached images
2. Images are sent to Google Gemini for analysis
3. Gemini extracts structured match data (map, mode, kills, deaths, etc.)
4. Results are saved to MongoDB
5. A formatted response is sent back to the Discord channel

**Example:**
```
!stats
[attach screenshot images]
```

:::tip
For best results, use clear, uncropped screenshots of the post-match scoreboard.
:::

---

## `!query`

Query your match history using natural language, powered by Gemini AI.

**Usage:**
```
!query <your question>
```

**Examples:**
```
!query how many kills did I get on Raid?
!query what's my best KD ratio?
!query show my last 5 matches
```

**What happens:**
1. Your natural language question is sent to Gemini
2. Gemini translates it into a MongoDB query
3. The query is executed against your match data
4. Results are formatted and returned to Discord

:::note
Queries only return data from matches that have been previously analyzed with `!stats`.
:::

---

:::info[Gemini Response Sanitisation]
All responses from Gemini AI are validated against strict Pydantic schemas before being processed. For `!stats`, the extracted game data must conform to the [`GameStatsResponse`](/docs/schemas#gamestatsresponse) schema — enforcing correct types, value ranges, and enum membership. For `!query`, the generated MongoDB pipeline is validated against the [`MongoPipeline`](/docs/schemas#mongopipeline) schema, which restricts operations to a safe allowlist of read-only [aggregation operators](/docs/schemas#allowed_aggregation_operators) (`$match`, `$group`, `$project`, `$sort`, `$limit`, `$skip`, `$unwind`). Any response that fails validation is rejected.
:::
