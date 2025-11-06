#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
เติม BPM โดยไม่พึ่ง Jamendo API:
- ใช้ url หน้า track เดิม -> หาไฟล์พรีวิวเสียงจากหน้าเว็บ/ลิงก์ storage ที่เป็น pattern
- ดาวน์โหลดตัวอย่างเสียง -> ใช้ librosa ประมาณค่าจังหวะ (BPM)

Usage (ทดสอบ 5 แถวก่อน):
  python -u estimate_bpm_from_page.py ^
    --in "jamendo_16genres_cc_FULL_keepldups.csv" ^
    --out "jamendo_with_bpm.csv" ^
    --max_rows 5 ^
    --duration 30 ^
    --verbose
"""
import argparse, csv, os, re, sys, tempfile
from urllib.parse import urlparse
import requests, numpy as np, librosa

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JamendoBPM/1.2"}
ID_RE = re.compile(r'(?:/track/|/t/)(\d+)')
AUDIO_RE = re.compile(
    r"https://prod-\d+\.storage\.jamendo\.com/(?:download|stream)/(?:track|t)/(\d+)/(?:mp3\d?|mp32|mp31|mp3)/?[^\s\"']*",
    re.IGNORECASE,
)

def parse_track_id(url: str):
    if not url:
        return None
    m = ID_RE.search(url)
    return m.group(1) if m else None

def guess_storage_urls(track_id: str):
    """เดาชุด URL storage ยอดนิยมของ Jamendo (ลองหลายโปรด/หลายฟอร์แมต)"""
    prods = [1,2,3,4]
    fmts  = ["mp32","mp31","mp3"]
    basepaths = ["download/track", "stream/track", "download/t", "stream/t"]
    for p in prods:
        for bp in basepaths:
            for fm in fmts:
                yield f"https://prod-{p}.storage.jamendo.com/{bp}/{track_id}/{fm}/"

def fetch_html(url, timeout=(10,30)):
    r = requests.get(url, timeout=timeout, headers=UA)
    r.raise_for_status()
    return r.text

def find_audio_from_html(html, prefer_id=None):
    """หา URL เสียงจาก HTML ของหน้า track"""
    cand = []
    for m in AUDIO_RE.finditer(html):
        tid = m.group(1)
        u   = m.group(0)
        if prefer_id and tid != str(prefer_id):
            continue
        cand.append(u)
    return list(dict.fromkeys(cand))  # unique & keep order

def check_head(url, timeout=(8,20)):
    try:
        h = requests.head(url, allow_redirects=True, timeout=timeout, headers=UA)
        if 200 <= h.status_code < 400:
            return True, h.headers.get("content-type",""), int(h.headers.get("content-length","0") or 0)
    except Exception:
        pass
    return False, "", 0

def download_to(path, url, timeout=(10,60), verbose=False):
    with requests.get(url, stream=True, timeout=timeout, headers=UA) as r:
        r.raise_for_status()
        total = 0
        with open(path, "wb") as f:
            for ch in r.iter_content(65536):
                if ch:
                    f.write(ch)
                    total += len(ch)
    if verbose:
        print(f"  [dl] saved {total/1024:.1f} KB", file=sys.stderr)
    return total

def estimate_bpm_from_file(path, duration=45.0, sr=22050, verbose=False):
    y, sr = librosa.load(path, sr=sr, mono=True, duration=duration)
    if y.size == 0:
        if verbose: print("  [tempo] empty audio", file=sys.stderr)
        return None
    vals = []
    try:
        onset = librosa.onset.onset_strength(y=y, sr=sr)
        t1 = librosa.beat.tempo(onset_envelope=onset, sr=sr, aggregate=np.median)
        if t1 is not None and len(t1) > 0: vals.append(float(t1[0]))
    except Exception as e:
        if verbose: print(f"  [tempo] onset err: {e}", file=sys.stderr)
    try:
        t2, _ = librosa.beat.beat_track(y=y, sr=sr)
        if t2 and t2 > 0: vals.append(float(t2))
    except Exception as e:
        if verbose: print(f"  [tempo] beat_track err: {e}", file=sys.stderr)
    if not vals:
        if verbose: print("  [tempo] no candidates", file=sys.stderr)
        return None
    v = float(np.median(vals))
    if v < 60: v *= 2
    if v > 200: v /= 2
    if verbose: print(f"  [tempo] {vals} -> {v:.1f}", file=sys.stderr)
    return int(round(v))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max_rows", type=int, default=50)
    ap.add_argument("--duration", type=float, default=30.0)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    # load csv
    with open(args.inp, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fields = r.fieldnames or []

    if "bpm" not in fields:
        fields = fields + ["bpm"]
        for row in rows:
            row["bpm"] = row.get("bpm","")

    todo = [i for i, row in enumerate(rows) if not str(row.get("bpm","")).strip()]
    if args.max_rows and args.max_rows>0:
        todo = todo[:args.max_rows]

    print(f"[START] candidates without bpm = {len(todo)}", flush=True)

    tmpdir = tempfile.mkdtemp(prefix="bpm_")
    filled = 0

    for k, idx in enumerate(todo, start=1):
        row = rows[idx]
        title  = row.get("track_title","")
        artist = row.get("artist","")
        url    = row.get("url","")
        tid    = parse_track_id(url)

        print(f"[{k}/{len(todo)}] '{title[:40]}' / '{artist[:30]}'  id={tid}", flush=True)
        audio_url = None

        # A) เดา storage url ตรง ๆ ก่อน
        if tid:
            for cand in guess_storage_urls(tid):
                ok, ctype, clen = check_head(cand)
                if ok and (("audio" in ctype.lower()) or cand.endswith("/")):
                    audio_url = cand
                    if args.verbose:
                        print(f"  [probe] storage ok: {cand}  ({ctype}, {clen}B)", file=sys.stderr)
                    break

        # B) ถ้ายังไม่เจอ -> โหลด HTML แล้ว regex หา
        if not audio_url and url:
            try:
                html = fetch_html(url)
                cands = find_audio_from_html(html, prefer_id=tid)
                if args.verbose:
                    print(f"  [html] found {len(cands)} candidate audio urls", file=sys.stderr)
                for cu in cands:
                    ok, ctype, clen = check_head(cu)
                    if ok and "audio" in ctype.lower():
                        audio_url = cu
                        if args.verbose:
                            print(f"  [probe] html audio ok: {cu}  ({ctype}, {clen}B)", file=sys.stderr)
                        break
            except Exception as e:
                if args.verbose:
                    print(f"  [html] fetch err: {e}", file=sys.stderr)

        if not audio_url:
            print("  [skip] no audio url", flush=True)
            continue

        # ดาวน์โหลด/วัด bpm
        ext = ".mp3" if ".mp3" in audio_url else ".m4a"
        save = os.path.join(tmpdir, f"{tid or 'track'}{ext}")
        try:
            size = download_to(save, audio_url, verbose=args.verbose)
            if size < 8*1024:
                print("  [skip] tiny audio", flush=True)
                continue
            bpm = estimate_bpm_from_file(save, duration=args.duration, verbose=args.verbose)
            if bpm:
                row["bpm"] = str(bpm)
                filled += 1
                print(f"  [OK] bpm(audio) = {bpm}", flush=True)
            else:
                print("  [NO TEMPO]", flush=True)
        except Exception as e:
            print(f"  [ERR] {e}", flush=True)

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"[DONE] filled {filled} rows -> {args.out}", flush=True)

if __name__ == "__main__":
    main()
