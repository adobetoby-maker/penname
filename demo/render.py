#!/usr/bin/env python3
"""Render a penname demo chapter in Jason Keiller's voice.

Direct port of fractured-path/audio/render_chapter.py's pipeline (same
engine, same voice, same seed, same chunk/stitch/declick logic) adapted to
take an explicit input .md / output .mp3 pair instead of a book/chapter
number, since these are standalone demo scenes, not book chapters.

  python3 render.py <input.md> <output.mp3>
  python3 render.py <input.md> <output.mp3> --dry    # chunk only, no API calls
"""
import hashlib, json, os, re, ssl, subprocess, sys, time, urllib.error, urllib.request

VOICE = "powBJzjz7VpBtyzNZUJy"          # Jason Keiller - Audience Pleaser
MODEL = "eleven_multilingual_v2"
SEED  = 20260827
MAX_CHARS = 1800
BITRATE = 64
STITCH = 3
SR = 44100
WORK = "/tmp/penname_render"

# Stitched-Keiller band (fractured-path chapters 4+, request-stitched):
# 9,836 w/hr median, 9,700-9,994 observed range. Gate widened to 9,400-10,400
# per the ticket to allow for these being standalone scenes (cold open/close,
# no adjoining chapter momentum) rather than mid-book chapters.
GATE_LO, GATE_HI = 9400, 10400


def chunk(text):
    """Split on paragraph boundaries only."""
    out, cur = [], ""
    for p in (p.strip() for p in text.split("\n\n")):
        if not p:
            continue
        cand = (cur + "\n\n" + p).strip()
        if len(cand) > MAX_CHARS and cur:
            out.append(cur); cur = p
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def prep(path):
    t = open(path).read()
    t = re.sub(r"^#\s*Chapter\s*(\d+)\s*[—–:-]?\s*(.*)$",
               lambda m: f"Chapter {int(m.group(1))}. {m.group(2).strip()}.", t,
               count=1, flags=re.M)
    t = re.sub(r"^#{1,6}\s*", "", t, flags=re.M)          # strip heading marks
    t = re.sub(r"(\*\*|\*|`|_)", "", t)                   # strip emphasis marks
    t = re.sub(r"(?m)^\s*[-–—]{3,}\s*$", "", t)           # rules
    t = re.sub(r"(?im)^\s*end of chapter\b.*$", "", t)
    t = re.sub(r"(?im)^\s*\(?word count[:\s].*$", "", t)
    # Deviation (auto-fixed, in-scope): both demo scenes were extracted from a
    # larger source doc, leaving stray HTML-comment boundary markers ("-->" at
    # the top of scene 3, "<!--" at the bottom) that are not prose, not a
    # heading, not emphasis -- render_chapter.py's regex set never has to
    # handle this because real book chapters don't carry it. Left as-is these
    # get sent to the TTS engine as literal text. System-text blocks (FRAGMENT
    # ACQUIRED / FRAGMENT SILENT) are real prose and are NOT touched here.
    t = re.sub(r"(?m)^\s*-->\s*$", "", t)
    t = re.sub(r"(?m)^\s*<!--\s*$", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t, chunk(t)


def say(text, prev_ids, next_text, dest):
    body = {"text": text, "model_id": MODEL, "seed": SEED,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75,
                               "style": 0.0, "speed": 1.0}}
    if prev_ids:
        body["previous_request_ids"] = prev_ids[-STITCH:]
    if next_text:
        body["next_text"] = next_text[:400]
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(),
        headers={"xi-api-key": os.environ["ELEVEN_API_KEY"],
                 "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, context=ssl.create_default_context()) as r:
                open(dest, "wb").write(r.read())
                return r.headers.get("request-id"), r.headers.get("character-cost")
        except urllib.error.HTTPError as e:
            body_txt = e.read()[:500]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1)); continue
            sys.exit(f"  chunk failed HTTP {e.code}: {body_txt}")


def declick(src, dst):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-ac", "1", "-ar", str(SR), "-af",
                    "areverse,atrim=start=0.030,asetpts=N/SR/TB,"
                    "afade=t=in:st=0:d=0.060,areverse",
                    "-c:a", "pcm_s16le", dst, "-y"], check=True)


def dur(f):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", f], capture_output=True, text=True).stdout)


def main():
    src, out = sys.argv[1], sys.argv[2]
    dry = "--dry" in sys.argv
    text, chunks = prep(src)
    words = len(text.split())
    print(f"  {os.path.basename(src)}: {words:,} words, {len(chunks)} chunks, "
          f"{sum(len(c) for c in chunks):,} chars")
    if dry:
        for i, c in enumerate(chunks, 1):
            print(f"    {i:02d} {len(c):>5}ch  {c[:60].splitlines()[0]}...")
        return

    tag = os.path.splitext(os.path.basename(out))[0]
    d = os.path.join(WORK, tag); os.makedirs(d, exist_ok=True)
    ids, wavs, total_cost = [], [], 0
    for i, c in enumerate(chunks, 1):
        nxt = chunks[i] if i < len(chunks) else None
        raw = os.path.join(d, f"{i:02d}_raw.mp3")
        wav = os.path.join(d, f"{i:02d}.wav")
        rid, cost = say(c, ids, nxt, raw)
        if rid:
            ids.append(rid)
        if cost:
            total_cost += int(cost)
        declick(raw, wav)
        wavs.append(wav)
        print(f"    {i:02d}/{len(chunks)}  {dur(wav):6.1f}s  stitch={len(ids[-STITCH:])}  cost={cost}")

    lst = os.path.join(d, "list.txt")
    open(lst, "w").write("".join(f"file '{w}'\n" for w in wavs))
    joined = os.path.join(d, "joined.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", joined, "-y"], check=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", joined, "-c:a", "libmp3lame",
                    "-b:a", f"{BITRATE}k", "-ar", str(SR), "-ac", "1", out, "-y"], check=True)

    d_s = dur(out); rate = words / (d_s / 3600)
    in_band = GATE_LO <= rate <= GATE_HI
    print(f"\n  wrote {out}")
    print(f"  {os.path.getsize(out)/1e6:.1f} MB  {d_s/60:.1f} min  "
          f"{words:,} words  {rate:.0f} w/hr  total_credit_cost={total_cost}")
    print(f"  gate {GATE_LO}-{GATE_HI} w/hr: {'PASS' if in_band else 'OUT OF BAND -- investigate'}")


if __name__ == "__main__":
    main()
