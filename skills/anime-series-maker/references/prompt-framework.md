# Clip prompt framework

`scripts/build_prompt.py` assembles this from `series.json` + `episode.json`. This file explains each block so you can
write good episode fields and fix a prompt by hand when needed.

Order matters — the model weighs the start of the prompt most:

| # | Block | Comes from | Why |
|---|---|---|---|
| 1 | **Opening directive** — "Create a continuous N-second {genre} scene. Follow the exact shot pacing…" | series `genre`, `tone`, clip `duration` | Sets length, genre and that this is ONE continuous scene |
| 2 | **Reference mapping** — "@material:123 = character sheet of the BLONDE GIRL (use only her design…). The sheets are design references only — never show the sheet layout…" | `characters[].material`, `label` | Without "never show the sheet" models sometimes paste the white sheet panel into frame |
| 3 | **Character consistency** — one paragraph per character: label, sheet, full `look`, `personality`, "Same design in every frame." | `characters[]` | Re-stating every visible detail is what keeps hair length and outfits from drifting |
| 4 | **STYLE:** | series `style` | Pure style keywords + "everything must be hand-drawn 2D" clamp |
| 5 | **VOICES & AUDIO:** language + one voice line per character + music/SFX bed | `language`, `characters[].voice`, `audio` | Gives each character a distinct, gendered voice in the right language |
| 6 | **Setting continuity** | clip `setting` (index or text) | One location per clip keeps palette and lighting stable |
| 7 | **FOCUS:** | clip `focus` | Theme / emotion keywords |
| 8 | **CHARACTER DESIGN:** how each character's expression changes across the clip | clip `arcs` | Gives the model an emotional arc, not just poses |
| 9 | **Shot list** — `[0s – 3s] SHOT 1 — TITLE. action` / `Dialogue:` / `SFX:` / `Camera:` | clip `shots[]` | Per-shot timing, line, sound and camera — the core control surface |
| 10 | **FINAL VISUAL:** + "On-screen ending mood:" | clip `final_visual`, `ending_mood` | A clean last frame = a clean cut point |
| 11 | **No-text block** + closing statement | series `negative`, `closing` | Keep it short: no subtitles / on-screen text / speech bubbles |

## Writing shots

- ~1 shot per 2–3 s. 15 s ≈ 5–7 shots. More shots = faster comedy, but each needs a clear single action.
- `action`: start with shot size (Wide / Medium / Close-up / Over-shoulder), then ONE action, then the background detail.
- `dialogue`: `Speaker (delivery): 「line」`. Several speakers in one shot are fine. No dialogue → `No spoken dialogue`.
  Japanese lines in 「」 work well; keep each ≤ ~15 characters / ~2.5 s.
- `sfx`: concrete sounds ("glasses glint ting", "comedic boing", "crow caw").
- `camera`: one movement per shot: push-in, pull-out, pan, whip pan, tracking, static, low angle, over-shoulder. **No rotating/orbit moves** in short clips.
- Small, readable actions beat big ones: peeking, blushing, pushing up glasses, storming off. Avoid long running/fighting choreography.
- Emotions as visible actions ("covers her face with both hands"), not adjectives ("very embarrassed").

## Worked example (built from `templates/episode.json`)

```
Create a continuous 15-second 2D anime romantic comedy scene. Follow the exact shot pacing, comedic timing and emotional rhythm below, with smooth scene continuity from shot to shot. fast, punchy anime comedy timing with expressive faces and snappy reactions.
Reference mapping: @material:111 = character sheet of the BLONDE GIRL (use only her design: face, hair, outfit, shoes). @material:222 = character sheet of the BOY WITH GLASSES (use only his design: face, hair, outfit, shoes). The sheets are design references only — never show the sheet layout, white background, panels or any text from them.

Maintain exact character consistency throughout all shots —
The BLONDE GIRL (@material:111): very long straight platinum-blonde hair to her thighs … Same design in every frame.
The BOY WITH GLASSES (@material:222): messy jet-black hair, thin round wire-rimmed glasses … Same design in every frame.

STYLE: 2D Japanese anime, soft cel shading, clean thin lineart, …
VOICES & AUDIO: All dialogue is spoken in natural JAPANESE by anime voice actors with clear lip-sync. BLONDE GIRL: bright high-pitched ojou-sama voice … BOY WITH GLASSES: clean calm youthful tenor … Light whimsical orchestral pizzicato comedy music, anime comedy SFX.
Preserve continuity of the setting: sunlit gothic stone corridor with tall arched windows … — consistent palette and lighting across the entire scene.

FOCUS: tsundere rich girl, fake fall to be caught, awkward stiff catch, …

CHARACTER DESIGN:
BLONDE GIRL — plotting and nervous at first, then cringing at herself, …
BOY WITH GLASSES — calm and oblivious-looking, catches her like a stiff wooden plank …
[0s – 3s] SHOT 1 — THE STAKEOUT. Medium close-up: the blonde girl peeks out from behind a stone pillar …
Dialogue: Girl (whispering to herself): 「…いい？彼が来たら、か弱く倒れて…受け止めてもらうだけ。」
SFX: soft footsteps echoing far away, fabric rustle. Camera: slow push-in on her face.
…
FINAL VISUAL: he goes back to his book with a small smile while her blonde hair whips out of frame as she storms off.
On-screen ending mood: playful embarrassment — her plan failed, but she is not giving up.
NO SUBTITLES. NO ON-SCREEN TEXT OR CAPTIONS. NO SPEECH BUBBLES.
All dialogue must exist only as natural in-scene Japanese audio. …
```
