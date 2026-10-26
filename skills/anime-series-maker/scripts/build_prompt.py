#!/usr/bin/env python3
"""Build and validate one prompt per clip from series.json + episode.json.

    python3 build_prompt.py series.json ep07/episode.json [--out ep07/prompts]

Writes <out>/clipNN.txt and <out>/tasks.json (model, duration, ratio, references per clip,
ready to hand to estimate_cost / create_tasks). Exits 1 on any validation error and writes nothing.
Python 3 stdlib only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"material:0+\b|【|】|\{\{|\}\}|TODO|TBD|<[A-Z_ ]+>")


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        sys.exit(f"ERROR: cannot read {path}: {e}")


def cap(text):
    """Capitalise the first letter and end with a full stop (empty stays empty)."""
    text = text.strip().rstrip(".")
    return f"{text[0].upper()}{text[1:]}." if text else ""


def fmt_t(x):
    return f"{x:g}s"


def build_clip(series, clip, cast):
    lang = series.get("language", "Japanese")
    dur = clip["duration"]
    lines = []
    lines.append(
        f"Create a continuous {dur}-second {series.get('genre', '2D anime')} scene. "
        "Follow the exact shot pacing, comedic timing and emotional rhythm below, with smooth scene "
        f"continuity from shot to shot. {cap(series.get('tone', ''))}".strip()
    )
    mapping = " ".join(
        f"@{c['material']} = character sheet of the {c['label']} (use only this design: face, hair, outfit, shoes)."
        for c in cast
    )
    lines.append(
        f"Reference mapping: {mapping} The sheets are design references only — never show the sheet "
        "layout, white background, panels or any text from them."
    )
    lines.append("")
    lines.append("Maintain exact character consistency throughout all shots —")
    for c in cast:
        lines.append(
            f"The {c['label']} (@{c['material']}): {c['look'].rstrip('.')}. "
            f"{cap(c['personality'])} Same design in every frame."
        )
    lines.append("")
    lines.append(f"STYLE: {series['style']}")
    voices = " ".join(f"{c['label']}: {c['voice'].rstrip('.')}." for c in cast)
    lines.append(
        f"VOICES & AUDIO: All dialogue is spoken in natural {lang.upper()} by anime voice actors with clear "
        f"lip-sync. {voices} {series.get('audio', '')}".strip()
    )
    setting = clip.get("setting", "")
    if isinstance(setting, int):
        setting = series["settings"][setting]
    lines.append(
        f"Preserve continuity of the setting: {setting} — consistent palette and lighting across the entire scene."
    )
    lines.append("")
    lines.append(f"FOCUS: {clip['focus']}")
    lines.append("")
    lines.append("CHARACTER DESIGN:")
    for c in cast:
        arc = clip.get("arcs", {}).get(c["id"])
        if arc:
            lines.append(f"{c['label']} — {arc}")
    for i, s in enumerate(clip["shots"], 1):
        a, b = s["t"]
        lines.append(f"[{fmt_t(a)} – {fmt_t(b)}] SHOT {i} — {s['title'].upper()}. {s['action']}")
        lines.append(f"Dialogue: {s.get('dialogue') or 'No spoken dialogue.'}")
        lines.append(f"SFX: {s['sfx'].rstrip('.')}. Camera: {s['camera'].rstrip('.')}.")
    lines.append("")
    lines.append(f"FINAL VISUAL: {clip['final_visual']}")
    lines.append(f"On-screen ending mood: {clip['ending_mood']}")
    lines.append(series.get("negative", "NO SUBTITLES. NO ON-SCREEN TEXT OR CAPTIONS. NO SPEECH BUBBLES."))
    lines.append(series.get("closing", "").replace("{language}", lang))
    return "\n".join(lines).strip() + "\n"


def validate(series, ep):
    errs = []
    chars = {c["id"]: c for c in series.get("characters", [])}
    for c in chars.values():
        for k in ("label", "material", "look", "personality", "voice"):
            if not str(c.get(k, "")).strip():
                errs.append(f"character '{c['id']}': missing {k}")
        if not re.fullmatch(r"material:[1-9]\d*", str(c.get("material", ""))):
            errs.append(f"character '{c['id']}': material must be 'material:<id>' of the uploaded sheet (got {c.get('material')!r})")
        if len(c.get("look", "")) < 120:
            errs.append(f"character '{c['id']}': look is too short — restate hair, eyes, every outfit piece, shoes, props")
    if not series.get("style"):
        errs.append("series: style is empty")
    clips = ep.get("clips", [])
    if not clips:
        errs.append("episode: no clips")
    max_dur = series.get("max_clip_seconds", 15)
    for n, clip in enumerate(clips, 1):
        tag = f"clip {n:02d}"
        dur = clip.get("duration", 0)
        if not 1 <= dur <= max_dur:
            errs.append(f"{tag}: duration {dur} outside 1–{max_dur}s (set series.max_clip_seconds from list_models)")
        for cid in clip.get("cast", []):
            if cid not in chars:
                errs.append(f"{tag}: unknown cast id '{cid}'")
        if not clip.get("cast"):
            errs.append(f"{tag}: empty cast")
        for k in ("focus", "final_visual", "ending_mood"):
            if not str(clip.get(k, "")).strip():
                errs.append(f"{tag}: missing {k}")
        st = clip.get("setting", "")
        if isinstance(st, int) and not 0 <= st < len(series.get("settings", [])):
            errs.append(f"{tag}: setting index {st} not in series.settings")
        prev_end = 0
        shots = clip.get("shots", [])
        if not shots:
            errs.append(f"{tag}: no shots")
        for i, s in enumerate(shots, 1):
            for k in ("t", "title", "action", "sfx", "camera"):
                if not s.get(k):
                    errs.append(f"{tag} shot {i}: missing {k}")
            if "dialogue" not in s:
                errs.append(f"{tag} shot {i}: missing dialogue (use \"\" for none)")
            t = s.get("t") or [0, 0]
            if len(t) != 2 or t[0] >= t[1]:
                errs.append(f"{tag} shot {i}: bad time range {t}")
                continue
            if abs(t[0] - prev_end) > 0.01:
                errs.append(f"{tag} shot {i}: starts at {t[0]}s but previous shot ends at {prev_end}s")
            prev_end = t[1]
        if shots and abs(prev_end - dur) > 0.01:
            errs.append(f"{tag}: shots end at {prev_end}s but duration is {dur}s")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("series")
    ap.add_argument("episode")
    ap.add_argument("--out", help="output folder (default: <episode dir>/prompts)")
    args = ap.parse_args()

    series, ep = load(args.series), load(args.episode)
    errs = validate(series, ep)
    chars = {c["id"]: c for c in series.get("characters", [])}
    prompts = []
    if not errs:
        for n, clip in enumerate(ep["clips"], 1):
            cast = [chars[cid] for cid in clip["cast"]]
            p = build_clip(series, clip, cast)
            if len(p) < 1500:
                errs.append(f"clip {n:02d}: prompt only {len(p)} chars — something is missing")
            m = PLACEHOLDER.search(p)
            if m:
                errs.append(f"clip {n:02d}: placeholder left in prompt: {m.group(0)!r}")
            prompts.append((n, clip, cast, p))
    if errs:
        print("NOT BUILT — fix these first:", file=sys.stderr)
        for e in errs:
            print("  -", e, file=sys.stderr)
        sys.exit(1)

    out = Path(args.out) if args.out else Path(args.episode).parent / "prompts"
    out.mkdir(parents=True, exist_ok=True)
    tasks = []
    for n, clip, cast, p in prompts:
        (out / f"clip{n:02d}.txt").write_text(p, encoding="utf-8")
        task = {
            "label": f"{ep.get('id', 'ep')} clip {n:02d}",
            "idempotencyKey": f"{ep.get('id', 'ep')}-clip{n:02d}",
            "duration": clip["duration"],
            "ratio": series.get("ratio", "16:9"),
            "audioGeneration": True,
            "references": [{"ref": c["material"], "role": "reference_image"} for c in cast],
            "promptFile": str(out / f"clip{n:02d}.txt"),
        }
        if series.get("model"):
            task["model"] = series["model"]
        if series.get("resolution"):
            task["resolution"] = series["resolution"]
        tasks.append(task)
        print(f"OK clip{n:02d}.txt  {clip['duration']}s  {len(clip['shots'])} shots  {len(p)} chars  cast={[c['id'] for c in cast]}")
    (out / "tasks.json").write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(c["duration"] for c in ep["clips"])
    print(f"{len(prompts)} clips, {total}s total -> {out}/tasks.json")


if __name__ == "__main__":
    main()
