#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ดึงเพลงจาก Jamendo ครบ 16 แนว โดยใช้ search (กว้างกว่า tags)
- รองรับ pagination
- เติม BPM (ถ้ามีใน musicinfo)
- ใส่ license filter ได้ (ใส่เฉพาะตอนระบุ)
การใช้งาน (ตัวอย่าง):
  python fetch_jamendo_16genres_search.py --client_id YOUR_ID --per_genre 100 --out jamendo_16genres.csv
  # ถ้าจะกรองลิขสิทธิ์:
  python fetch_jamendo_16genres_search.py --client_id YOUR_ID --per_genre 100 --licenses ccplus,cc-by,cc-zero --out jamendo_16genres.csv
"""
import argparse, csv, time, sys
import requests

GENRE_QUERIES = {
    "Rock":       'rock OR "alt rock" OR altrock OR indierock OR punk OR grunge OR "classic rock" OR "hard rock"',
    "Pop":        'pop OR teenpop OR dancepop OR electropop OR synthpop OR indiepop OR "chart pop" OR ballad OR "mainstream pop" OR "radio edit"',
    "Metal":      'metal OR "heavy metal" OR thrash OR metalcore OR deathcore OR "power metal" OR "black metal"',
    "Classical":  'classical OR orchestra OR symphony OR piano OR chamber OR baroque OR romantic OR concerto',
    "Video game music": 'chiptune OR chipmusic OR "8 bit" OR 8bit OR 16bit OR vgm OR "game music" OR "video game" OR "game soundtrack" OR ost OR "retro game" OR arcade OR nes OR gameboy',
    "EDM":        'edm OR house OR "progressive house" OR "electro house" OR techno OR trance OR "progressive trance" OR dance OR club OR dubstep OR "drum and bass" OR dnb',
    "R&B":        '"r&b" OR rnb OR soul OR "contemporary r&b"',
    "Hip hop":    'hiphop OR "hip hop" OR rap OR trap OR "boom bap" OR drill',
    "Folk":       'folk OR acoustic OR "singer songwriter" OR "indie folk" OR "neo folk" OR bluegrass',
    "K pop":      'kpop OR "k-pop" OR "korean pop" OR krnb OR "k hiphop" OR "k-hiphop" OR "k indie" OR "k ballad"',
    "Country":    'country OR americana OR bluegrass OR "alt country"',
    "Rap":        'rap OR hiphop OR trap OR drill',
    "Jazz":       'jazz OR swing OR bebop OR "latin jazz" OR "cool jazz" OR "smooth jazz" OR "hard bop"',
    "Lofi":       'lofi OR "lo-fi" OR chillhop OR chill OR "study beats" OR "lofi hip hop"',
    "Gospel":     'gospel OR choir OR "worship music"',
    "Latin":      'latin OR reggaeton OR salsa OR merengue OR bachata OR cumbia OR "latin pop" OR "latin trap"',
}


def fetch_genre(client_id, query, per_genre, licenses="", limit=200, max_pages=20, verbose=True):
    rows, offset, pages = [], 0, 0
    while len(rows) < per_genre and pages < max_pages:
        params = {
            "client_id": client_id,
            "format": "json",
            "limit": limit,
            "offset": offset,
            "order": "popularity_total",
            "include": "musicinfo",
            "search": query,          # ใช้ SEARCH (กว้างกว่า tags)
        }
        if licenses:
            params["license"] = licenses  # ใส่เฉพาะเมื่อระบุ
        r = requests.get("https://api.jamendo.com/v3.0/tracks", params=params, timeout=35)
        if verbose:
            print("[HTTP]", r.url, file=sys.stderr)
        r.raise_for_status()
        data = r.json().get("results", [])
        if verbose:
            print(f"[PAGE @ {offset}] got {len(data)}", file=sys.stderr)
        if not data:
            break
        for t in data:
            if len(rows) >= per_genre:
                break
            mi = t.get("musicinfo") or {}
            rh = mi.get("rhythm") or {}
            rows.append({
                "track_title": (t.get("name") or "").strip(),
                "artist": (t.get("artist_name") or "").strip(),
                "bpm": rh.get("bpm",""),
                "duration_sec": int(float(t.get("duration",0))) if t.get("duration") else "",
                "license": (t.get("license") or "").upper(),
                "source": "Jamendo",
                "url": t.get("shareurl",""),
                "notes": ""
            })
        offset += limit
        pages += 1
        time.sleep(0.35)  # กัน rate limit เล็กน้อย
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client_id", required=True)
    ap.add_argument("--per_genre", type=int, default=100)
    ap.add_argument("--licenses", default="")  # ใส่เช่น ccplus,cc-by,cc-zero  (สะกดแบบนี้เท่านั้น)
    ap.add_argument("--out", default="jamendo_16genres.csv")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    fields = ["genre","index_in_genre","track_title","artist","bpm","duration_sec","license","source","url","notes"]
    total = 0
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for genre, query in GENRE_QUERIES.items():
            if args.verbose:
                print(f"[INFO] {genre} :: {query}", file=sys.stderr)
            data = fetch_genre(args.client_id, query, args.per_genre, licenses=args.licenses, verbose=args.verbose)
            for i, t in enumerate(data, start=1):
                w.writerow({"genre": genre, "index_in_genre": i, **t})
            if args.verbose:
                print(f"[OK] {genre}: wrote {len(data)} rows", file=sys.stderr)
            total += len(data)
    print(f"[DONE] wrote {total} rows to {args.out}")

if __name__ == "__main__":
    main()
