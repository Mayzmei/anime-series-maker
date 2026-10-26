#!/usr/bin/env python3
"""Join generated clips into one postable episode.

    python3 assemble.py clip01.mp4 clip02.mp4 clip03.mp4 -o ep07_final.mp4 \
        [--trim 1:0.2:0.4] [--clip-db 0] [--bgm music.mp3 --bgm-db -20] \
        [--watermark logo.png --wm-width 130 --wm-opacity 0.6] [--vertical] [--fps 30]

- --trim N:HEAD:TAIL  cut HEAD seconds from the start and TAIL from the end of clip N (1-based); repeatable.
- Every clip is normalised (scale + pad to 1080p, fps, yuv420p tv range, SAR 1, bt709) and the whole episode is
  encoded ONCE. Never join AI clips with `-c copy`: mixed pixel formats / colour ranges make Instagram drop segments.
- 1080p = lanczos scale + light unsharp. Audio: generated dialogue kept, optional looped BGM bed underneath,
  fade-out, loudness normalised to -14 LUFS.
- Afterwards it decodes the file end-to-end and writes <out>_joins.jpg (frames just before / after every cut).
Needs ffmpeg + ffprobe on PATH. Python 3 stdlib only.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERROR running {' '.join(cmd[:3])} …\n{r.stderr[-2000:]}")
    return r.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
               "-of", "json", str(path)])
    j = json.loads(out)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    if not v:
        sys.exit(f"ERROR: no video stream in {path}")
    return {"w": v["width"], "h": v["height"], "dur": float(j["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--trim", action="append", default=[])
    ap.add_argument("--clip-db", type=float, default=0.0, help="gain for the generated clip audio")
    ap.add_argument("--bgm")
    ap.add_argument("--bgm-db", type=float, default=-20.0)
    ap.add_argument("--watermark")
    ap.add_argument("--wm-width", type=int, default=130)
    ap.add_argument("--wm-opacity", type=float, default=0.6)
    ap.add_argument("--wm-margin", default="20:8", help="right:bottom margin in px")
    ap.add_argument("--vertical", action="store_true", help="force 1080x1920 (default: follow clip 1)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--lufs", type=float, default=-14.0)
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"ERROR: {tool} not found on PATH")
    clips = [Path(c) for c in args.clips]
    for c in clips:
        if not c.is_file():
            sys.exit(f"ERROR: missing clip {c}")
    info = [probe(c) for c in clips]

    trims = {}
    for t in args.trim:
        n, head, tail = t.split(":")
        trims[int(n)] = (float(head), float(tail))

    vertical = args.vertical or info[0]["h"] > info[0]["w"]
    W, H = (1080, 1920) if vertical else (1920, 1080)

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for c in clips:
        cmd += ["-i", str(c)]
    idx = len(clips)
    if args.bgm:
        cmd += ["-stream_loop", "-1", "-i", args.bgm]
        bgm_idx, idx = idx, idx + 1
    if args.watermark:
        cmd += ["-i", args.watermark]
        wm_idx = idx

    fc, durs = [], []
    for i, inf in enumerate(info):
        head, tail = trims.get(i + 1, (0.0, 0.0))
        d = inf["dur"] - head - tail
        if d <= 0.3:
            sys.exit(f"ERROR: clip {i + 1} trimmed to {d:.2f}s")
        durs.append(d)
        fc.append(
            f"[{i}:v]trim=start={head}:duration={d},setpts=PTS-STARTPTS,"
            f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,unsharp=5:5:0.6:5:5:0.0,"
            f"fps={args.fps},scale=in_range=auto:out_range=tv,format=yuv420p,setsar=1[v{i}]"
        )
        if inf["audio"]:
            fc.append(f"[{i}:a]atrim=start={head}:duration={d},asetpts=PTS-STARTPTS,"
                      f"aresample=48000,aformat=channel_layouts=stereo,volume={args.clip_db}dB[a{i}]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={d}[a{i}]")
    n = len(clips)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    total = sum(durs)

    vlast = "vc"
    if args.watermark:
        mr, mb = args.wm_margin.split(":")
        fc.append(f"[{wm_idx}:v]scale={args.wm_width}:-1,format=rgba,colorchannelmixer=aa={args.wm_opacity}[wm]")
        fc.append(f"[vc][wm]overlay=W-w-{mr}:H-h-{mb}[vw]")
        vlast = "vw"

    alast = "ac"
    if args.bgm:
        fc.append(f"[{bgm_idx}:a]atrim=duration={total},aresample=48000,aformat=channel_layouts=stereo,"
                  f"volume={args.bgm_db}dB[bg]")
        fc.append("[ac][bg]amix=inputs=2:duration=first:normalize=0[am]")
        alast = "am"
    fade_st = max(total - 1.5, 0)
    fc.append(f"[{alast}]afade=t=out:st={fade_st}:d=1.5,loudnorm=I={args.lufs}:TP=-1.5:LRA=11,aresample=48000[aout]")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{vlast}]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", str(out)]
    run(cmd)

    # verify: full decode must be clean
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "null", "-"], capture_output=True, text=True)
    if r.stderr.strip():
        print("WARNING: decode errors:\n" + r.stderr[-1500:], file=sys.stderr)

    # contact sheet of every join
    joins, t = [], 0.0
    for d in durs[:-1]:
        t += d
        joins.append(t)
    sheet = out.with_name(out.stem + "_joins.jpg")
    if joins:
        with tempfile.TemporaryDirectory() as tmp:
            k = 0
            for j in joins:
                for ts in (max(j - 0.25, 0), j + 0.25):
                    k += 1
                    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(out), "-frames:v", "1",
                         "-vf", "scale=480:-2", f"{tmp}/f{k:03d}.jpg"])
            run(["ffmpeg", "-y", "-v", "error", "-i", f"{tmp}/f%03d.jpg",
                 "-vf", f"tile=2x{len(joins)}:padding=6:color=white", "-frames:v", "1", str(sheet)])
    print(f"OK {out}  {W}x{H}  {total:.2f}s  clips={n}" + (f"  joins sheet: {sheet}" if joins else ""))


if __name__ == "__main__":
    main()
