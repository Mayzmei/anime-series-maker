<div align="center">

# Anime Series Maker · AI 番剧连载

**2 character sheets + 1 line of story → a finished anime episode. Then the next one, with the same cast.**
Hook, shot-by-shot script, voiced anime clips, QA, edit, Instagram-safe cover and caption — run by your AI agent.

**English** · [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-SKILL.md-orange)
![Renoise MCP](https://img.shields.io/badge/video-Renoise%20MCP-ff7a1a)

<!-- TODO: docs/images/cover.jpg — a 2×2 grid of 4 episode frames -->
<img src="docs/images/cover.jpg" width="820" alt="Four episodes of the same AI anime series">

</div>

> I've been posting an AI fan-anime series on Instagram: 40+ episodes, one fixed cast, top episodes at **605k / 495k / 301k views**.
> This repo is that whole workflow packed into one skill, including every mistake that cost me credits along the way.

---

## Demos

<!-- TODO: replace with GIFs in docs/gifs/ + video links (GitHub Release assets) -->
| | | |
|:---:|:---:|:---:|
| **Fake-out fails in 3 s** · 14 s · 605k views | **Cat-girl transformation** · 63 s · 495k views | **Catchphrase ×3** · 72 s · 301k views |

---

## What it does

- **Series bible, not one-off prompts.** Cast, art style, voices, locations and running gags live in `series.json`. Episode 30 looks like episode 1.
- **Hook first.** Before writing anything, the agent pitches 3 premises with one pick, based on formulas ranked by real views (fake-out that fails, transformation, catchphrase ×3, "wants it, can't admit it"…).
- **Per-second shot scripts.** Each ≤15 s clip gets a shot list with action, in-character dialogue, SFX and camera for every shot, assembled into a long structured prompt. The prompt restates every design detail, so hair and outfits don't drift.
- **Validated before a single credit is spent.** `build_prompt.py` refuses to build if a sheet ID is missing, a placeholder is left, a shot has no camera, or timings don't add up.
- **Cost gate.** The agent quotes clips · seconds · credits · balance, waits for your "yes", generates clip 1 for you to check, *then* batches the rest.
- **QA every clip.** Character match against the sheets, burned-in subtitles, voice gender and language, story logic. A failed clip is regenerated whole, never patched.
- **Edit that survives Instagram.** One-pass re-encode with every clip normalised (AI clips joined with `-c copy` get segments dropped by IG), 1080p, optional BGM bed and watermark, −14 LUFS, and a contact sheet of every cut for you to check.
- **Cover + caption.** The cover is generated with the character sheets as references, so faces match. 9:16 with the title in Instagram's 3:4 grid safe zone, plus a crop preview. Captions use the hook format that actually got reach.
- **Learns from your views.** Every episode is logged; tell the agent your view counts and the next premises are ranked by them.

## How it works

```
0. setup check (Renoise MCP / ffmpeg / Python)
1. series bible — sheets, personalities, voices, style preset, language, ratio   (once per series)
2. hook — 3 premises, 1 pick
3. script — ≤15 s clips, 1 shot per 2–3 s, new in-character dialogue
4. build_prompt.py — assemble + validate every clip prompt
5. quote → your "yes" → clip 1 → you check → the rest
6. QA every clip → regenerate failures whole
7. assemble.py — trim, normalise, join, 1080p, BGM, loudness, join check
8. cover (sheets as refs) → cover_check.py
9. caption (IG / X)
10. log the episode (+ views later)
```

## Install

### 1 · Get the skill

```bash
git clone https://github.com/<YOUR_GITHUB>/anime-series-maker.git
```

**Claude Code**
```bash
mkdir -p ~/.claude/skills && cp -R anime-series-maker/skills/anime-series-maker ~/.claude/skills/
```
**Codex**
```bash
mkdir -p ~/.codex/skills && cp -R anime-series-maker/skills/anime-series-maker ~/.codex/skills/
```
**Other agents** (OpenClaw, WorkBuddy, …): import the `skills/anime-series-maker` folder (or a zip of it) on the product's Skills page.

### 2 · Connect Renoise (video / image generation)

Make an account at [renoise.ai](https://renoise.ai). Login happens in the browser, so there's no API key to paste.

| Agent | How |
|---|---|
| Claude Code | `/plugin marketplace add ArcoCodes/renoise-plugins-official` then `/plugin install renoise@renoise-plugins-official` |
| Codex | `codex mcp add renoise --url https://renoise.ai/api/public/mcp` then `codex mcp login renoise` |
| Claude desktop / claude.ai | Settings → Connectors → Add custom connector → URL `https://renoise.ai/api/public/mcp` |
| Others (Cursor, WorkBuddy, …) | add a remote MCP server: `https://renoise.ai/api/public/mcp` |

Latest instructions: [renoise.ai/plugin](https://renoise.ai/plugin). Test it by asking your agent to *"check my Renoise balance"*.

### 3 · Local tools

```bash
brew install ffmpeg            # Windows: winget install Gyan.FFmpeg · Linux: sudo apt install ffmpeg
python3 -m pip install pillow  # only for the cover check
```

## Use it

> *Make an anime series with these two character sheets: she's a proud rich-girl tsundere, he's calm and teases her. Japanese voices, soft watercolor style.*

> *Next episode. Something with her turning into a cat.*

The agent asks everything it needs in one message, shows the script and the credit quote, and doesn't spend anything until you say yes.

## Repo layout

```
skills/anime-series-maker/
  SKILL.md                     # the workflow the agent follows
  references/
    prompt-framework.md        # clip prompt structure + full example
    style-presets.md           # Soft Watercolor · Sharp Thick-Paint · Flat Cel · Live-Action
    hooks.md                   # premise formulas ranked by views, cover + caption patterns
    pitfalls.md                # every expensive mistake and its fix
  templates/series.json        # example series bible
  templates/episode.json       # example episode script
  scripts/build_prompt.py      # assemble + validate prompts → prompts/clipNN.txt + tasks.json
  scripts/assemble.py          # trim, normalise, join, 1080p, BGM, watermark, loudness, join sheet
  scripts/cover_check.py       # Instagram 3:4 grid crop preview
```

## Notes

- **Use characters you have the right to use.** Original characters are the safest. Prompts describe characters by appearance only, never by franchise names.
- Generation runs on your own Renoise credits. The skill always quotes before spending.
- Label AI content where your platform asks for it.

## License

MIT
