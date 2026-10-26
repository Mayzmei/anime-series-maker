---
name: anime-series-maker
description: Turn 2–3 character sheets + one line of story into a finished, postable 2D anime episode (15–90 s) — and keep making the next one with the same cast. Plans the hook, writes a per-second shot script with in-character dialogue, generates each ≤15 s clip on Renoise (Seedance-class video models via Renoise MCP), checks every clip, edits the cut, makes an Instagram-safe cover and writes the caption. Use when the user says "make an anime episode", "next episode", "anime series", "fan anime", "AI anime short", "番剧", "动漫短片", "下一集", "连载", "同人动画", "アニメ", or hands over character sheets and a story idea. NOT for remaking a specific reference video shot-for-shot (use a remake skill), or for realistic talking-head / UGC videos.
---

# Anime Series Maker

One series = one fixed cast, one fixed art style, one fixed voice setup, stored in `series.json`.
Every episode reuses it, so episode 30 looks like episode 1.

The pipeline was built while making a fan-anime series on Instagram (top episodes: 651K / 546K / 346K views).
Every rule in `references/pitfalls.md` is a mistake that cost real credits once. Read it before generating anything.

```
0. setup check ─► 1. series bible (once) ─► 2. hook ─► 3. script ─► 4. build + validate prompts
   ─► 5. quote credits → user says yes → clip 1 → user checks → rest
   ─► 6. QA every clip (retake whole clips) ─► 7. edit ─► 8. cover ─► 9. caption ─► 10. log episode
```

Work in a project folder chosen by the user (default `./my-series/`):

```
my-series/
  series.json            # the bible — cast, style, voices, settings, running gags
  sheets/                # character sheets (design references)
  episodes.json          # log of every episode: premise, hook, views (to avoid repeats, learn what works)
  ep07-cat-girl/
    episode.json         # the script
    prompts/clip01.txt … # built by scripts/build_prompt.py
    clips/clip01.mp4 …   # downloaded results
    ep07_final.mp4  ep07_cover.png  caption.md
```

---

## 0 · Setup check (skip what already works)

- **Renoise MCP** connected: call `get_account`. Balance 0 → stop and tell the user generation needs credits.
  Not connected → point them to the README "Connect Renoise" table.
- `ffmpeg` / `ffprobe` on PATH, `python3` with `Pillow` (`python3 -m pip install pillow`).
- Before choosing any model: `load_skill model-routing`, then `list_models` for the chosen model's real limits
  (max duration per clip, ratios, whether it generates audio). Don't trust model names from memory.

## 1 · Series bible (first time only)

Ask everything in **one** message:

1. **Cast** — 2–3 characters. Character sheets ready? (turnaround / full-body design sheets work best)
   - No sheets → generate them first (image model from model-routing, 1K, plain light background, front + side + back + 3 expressions, no text). Show them; iterate until approved. Sheets are the single biggest factor in consistency.
2. **Personality + voice** per character — one line each (e.g. "proud rich-girl tsundere, blushes instantly, voice cracks when flustered").
3. **Art style** — offer the presets in `references/style-presets.md` with a recommendation (default: Soft Watercolor).
4. **Dialogue language** — Japanese is the default for anime (sounds most "anime" to every audience); English / Chinese / Korean also work.
5. **Ratio** — 16:9 (YouTube / X, default) or 9:16 (Reels / TikTok / Shorts).

Then:
- Upload the sheets with `upload_files` → write each `material:<id>` into `series.json`.
- Fill `series.json` from `templates/series.json`. The `look` field must restate every visible design detail
  (hair length/colour/parting, eyes, uniform pieces, shoes, props). The model re-reads it every clip — vague looks drift.

## 2 · Hook first, then plot

Short anime lives or dies on the premise. Before writing any script, offer **3 one-line premises with one top pick**,
using `references/hooks.md` (formulas that actually got views: transformation, fake-out that fails in 3 seconds,
catchphrase ×3, "she wants X but can't admit it", a tiny everyday moment with the viewer as "you").
Check `episodes.json` so you never repeat a premise, and reuse running gags from `series.json`.

## 3 · Script → `episode.json`

Copy `templates/episode.json`. Rules:

- **Clips ≤ the model's max duration** (usually 15 s). An episode is 1–6 clips. Each clip must be a complete mini-scene with its own beat; the cut between clips is a hard scene cut, never mid-action.
- **About one shot per 2–3 s**, each with `action`, `dialogue`, `sfx`, `camera` (format in `references/prompt-framework.md`).
- **Dialogue in the series language, in character.** Short lines (≤ ~2.5 s spoken each). Write new lines — never translate or paraphrase lines from an existing show or video.
- **Start on the story.** No title card, no cold-open teaser. First shot = the situation.
- End each clip on a readable reaction (blush, smirk, door slam) — it gives the editor a clean cut point.
- Describe copyrighted characters only by appearance in prompts (the bible does this already); never put franchise or character names in prompts.

Show the user the script as a compact table (time · shot · line) and wait for approval or edits.

## 4 · Build + validate prompts

```bash
python3 scripts/build_prompt.py my-series/series.json my-series/ep07-cat-girl/episode.json
```

It writes `prompts/clipNN.txt` (opening directive → reference mapping → character consistency → STYLE → VOICES → setting → FOCUS → CHARACTER DESIGN → per-shot list → FINAL VISUAL → no-text block) and **exits non-zero** if anything is wrong: missing sheet IDs, placeholders left, a shot without Dialogue/SFX/Camera, shots past the clip duration, prompt suspiciously short.
Never submit if it fails. Never pass a prompt to `create_tasks` from a file you didn't just build and check.

## 5 · Quote → approve → clip 1 → rest

1. `estimate_cost` with every planned clip (model, duration, ratio, `audioGeneration: true`, the sheet references with role `reference_image`).
2. Show: clips · seconds · credits · balance. **Stop and wait for the user's explicit "yes" in chat.**
3. `create_tasks` for **clip 1 only**, `wait_tasks`, show it. Ask: characters right? voices right? style right?
4. Only then submit the remaining clips (one `create_tasks` call, ≤10 tasks, each with an `idempotencyKey` like `ep07-clip02`).

References: every clip gets **all** sheets of the characters who appear, in the order the prompt maps them
(`@material:<id>` in the prompt = the same material in `references`).

## 6 · QA every clip

`download_results` → `clips/clipNN.mp4`. For each clip check (use `analyze_media` on the task, plus your own frame grabs: `ffmpeg -ss <t> -i clip.mp4 -frames:v 1 f.jpg` at 4 points):

- [ ] Characters match the sheets (hair length & colour, eye colour, outfit, props). No sheet layout / white panels in frame.
- [ ] No subtitles, speech bubbles or garbled text burned in.
- [ ] Voices: right language, right gender per character, the scripted lines (not random ones).
- [ ] Story logic: who talks faces who; cause → effect reads; the last beat lands.
- [ ] Style stayed 2D (no sudden photoreal / 3D shots).

Fail → **regenerate the whole clip** (same prompt, or tighten the failing part). Never splice a partial retake into a clip — it never looks seamless. Tell the user what failed and the retake cost before resubmitting.

## 7 · Edit

```bash
python3 scripts/assemble.py my-series/ep07-cat-girl/clips/clip0{1,2,3}.mp4 -o my-series/ep07-cat-girl/ep07_final.mp4 \
    [--trim 1:0.2:0.4] [--bgm music.mp3 --bgm-db -20] [--watermark logo.png] [--vertical]
```

What it does (see the script header): trims dead air, normalises every clip (fps, pixel format, colour range, SAR),
joins with **one re-encode** (never `-c copy` — Instagram's transcoder drops segments when formats change mid-file),
exports 1080p (lanczos + light sharpen, no AI upscaling), optional BGM bed under the generated dialogue, loudness to −14 LUFS,
then decodes the result end-to-end and writes a contact sheet of every join (`*_joins.jpg`) — look at it.

Show the final cut to the user **before** making the cover.

## 8 · Cover

- Refs: **the character sheets first**, then one frame from the episode as the scene reference. Frames alone make faces drift toward thick-paint / dark rendering.
- Prompt the sheets' exact art style (copy the STYLE line) and the episode's key moment; describe characters by look, no names.
- 9:16 canvas, but Instagram's grid crops to 3:4: no title or faces in the top/bottom 15%; the scene must still run full-bleed to the edges (never ask for "plain background" there — models paint a white band).
- `python3 scripts/cover_check.py cover.png` → shows the 3:4 crop; check it before delivering.
- Follow `references/hooks.md` → "Cover" for title rules (or no text at all for 小红书-style covers).

## 9 · Caption

Use `references/hooks.md` → "Captions": first line = the premise as one plain sentence aimed at "you",
one punchline, a follow line, hashtags. Give each platform/language as its own code block.

## 10 · Log

Append to `episodes.json`: id, title, premise, hook line, clips, credits spent, date. When the user later tells you views,
store them — next time, rank premise formulas by real views, not by taste.

---

## Files

- `references/prompt-framework.md` — the clip prompt structure, with a full worked example
- `references/style-presets.md` — tested art-style blocks
- `references/hooks.md` — premise formulas, cover and caption patterns
- `references/pitfalls.md` — every expensive mistake and its fix (read before step 5)
- `templates/series.json`, `templates/episode.json`
- `scripts/build_prompt.py`, `scripts/assemble.py`, `scripts/cover_check.py` (Python 3 stdlib + ffmpeg; Pillow for the cover check)
