# Pitfalls (each one cost real credits once)

## Generation

| Symptom | Cause | Fix |
|---|---|---|
| Characters drift (hair shorter, different uniform) by clip 3 | `look` too vague, or a sheet missing from that clip's references | Restate every visible detail in `look`; attach every on-screen character's sheet to every clip |
| The white character-sheet layout appears inside the video | Model treats the sheet as a scene | Keep the "design references only — never show the sheet layout…" line (build_prompt.py adds it) |
| Garbled subtitles / speech bubbles burned in | Model imitates text on refs, or dialogue looks like captions | Keep the no-text block; sheets without text labels are safer. Diegetic text (a sign, a HUD) is fine if the story needs it |
| Wrong voice gender or language, or random lines | Weak voice block, or a **reference video's audio leaking** | One voice line per character with gender words; never attach a reference video with sound — strip it first: `ffmpeg -i in.mp4 -an -c:v copy ref_silent.mp4` |
| Photoreal background in one shot | Missing 2D clamp | Keep "EVERYTHING including all backgrounds must be hand-drawn 2D…" |
| Realistic lips / noses on anime faces | Style too painterly | Add "small simple anime mouths (no realistic lips), minimal nose, flat cel shading" |
| Moderation / copyright rejection | Franchise or character names in the prompt, or real-actor footage as reference | Describe characters by appearance only; for real-footage motion refs use a grayscale depth-map version of the clip |
| Batch submitted with an empty / wrong prompt (credits gone, running tasks can't be cancelled) | Shell loop read a prompt file that had moved | Only submit prompts `build_prompt.py` just built and validated; stop the batch on any failure |
| Image refs silently ignored | Some CLI paths rewrite the reference role | Use Renoise MCP `create_tasks` with `role: "reference_image"`; check the result actually follows the sheet |

## Editing

| Symptom | Cause | Fix |
|---|---|---|
| Instagram shows the video starting mid-way / drops a segment | Joined with `-c copy`; segments differ in pixel format or colour range (e.g. `yuvj420p` full range vs `yuv420p` tv range) | `assemble.py` re-encodes everything in one pass with identical fps / format / range / SAR. Also scrub through in the IG upload editor before posting |
| Partial retake looks like a glitch | A re-generated 3-second piece spliced into a clip | Re-generate the whole clip |
| Music jumps at every cut | Each clip has its own generated score | Turn the clip music down / out and lay one continuous BGM bed (`--bgm`) |
| Soft / blurry upload | Uploaded 720p | Export 1080p with lanczos + light unsharp (assemble.py default); no AI upscaling needed |
| Slow start, viewers scroll away | Title card or cold-open teaser | Start on the story; trim dead air (`--trim`) |

## Cover

| Symptom | Fix |
|---|---|
| Title cut off on the IG grid | Keep text in the 3:4 safe zone (see hooks.md); verify with `cover_check.py` |
| White / faded band at top | Never say "plain background"; ask for full-bleed scene to the edge |
| Faces don't look like the sheets (darker, heavier paint) | Pass the sheets first as references, frames only as scene reference |
