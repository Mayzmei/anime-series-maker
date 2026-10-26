# Hooks, covers and captions

## Premise formulas (ranked by real Instagram views of a 26-episode fan-anime series)

| Rank | Formula | Example premise | Views |
|---|---|---|---|
| 1 | **Fake-out that fails in 3 seconds** | She dresses up as a scary ghost to frighten him — her scary act lasts three seconds | 605k |
| 2 | **Transformation** (cat girl, kitten, tiny, swapped) | A spell goes wrong and she grows cat ears and a fluffy tail | 495k / 187k |
| 3 | **Catchphrase ×3** — the same line, escalating, three times | Every time something goes wrong she threatens "I'll tell my father" — the third time it backfires | 301k |
| 4 | **Wants X, can't admit it** | She wants a princess carry and keeps "accidentally" tripping near him | 237k |
| 5 | **Rescue / protect** | Someone bullies her; he steps in with one calm line | 196k |
| 6 | **Tiny rule / ritual** | She refuses to say the password to the dorm door | 129k |

Lower performers: long plot-heavy episodes (romance arcs, balls, multi-location stories) — beautiful, fewer views.
Short (14–30 s) single-joke episodes beat 60–100 s stories almost every time.

**Rules**
- One premise = one sentence a stranger understands with no context. If it needs "previously…", it's not a hook.
- The visual premise must be visible in the first 2 seconds (the cat ears, the ghost sheet, the trip).
- Recurring cute states (cat-girl form, a signature accessory) can become sub-series — repeat what got views.
- Offer 3 premises, one marked as the pick. After posting, log views in `episodes.json` and re-rank this table.

## Cover

- 9:16, but Instagram's profile grid shows a 3:4 center crop: title block from ~24% to ~38% of the height; no text or faces in the top/bottom 15%.
- The scene continues full-bleed to every edge — prompt "the scene and its colors extend all the way to the top edge; no fade, no white or blank band". Never "plain background".
- References: character sheets first, one episode frame as scene reference. Prompt the series STYLE line verbatim, plus "not heavy painting, not dark cinematic rendering" for soft styles.
- Title = the premise in ≤ 5 words (or no text at all for 小红书 / Xiaohongshu-style atmospheric covers, 3:4).
- No watermark on covers. Check with `scripts/cover_check.py`.

## Captions

Instagram:
```
<Character> <premise as one plain sentence, aimed at "you"> <emoji>

<one short punchline> <emoji>

follow for more episodes 🪄

<optional credit line: made on …>

#<series tag> #<character tags> #anime #AIVideo #AIanime …
```

X:
```
<Character> <premise sentence> <emoji>

<optional credit line>
```

What gets reach: a cute or absurd visual premise + "your" intimacy — "wakes up as a kitten on your pillow 🐱" —
not a plot recap, not "tries to … but fails". One punchline line only; no POV quotes.
Give every platform and language as its own code block.
