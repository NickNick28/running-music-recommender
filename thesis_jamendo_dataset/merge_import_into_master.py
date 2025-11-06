#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
รวม CSV สองไฟล์โดย:
- ต่อข้อมูลเข้าด้วยกัน
- ตัดซ้ำด้วยคอลัมน์ 'url'
- จัดเรียง และรีเซ็ต index_in_genre ต่อแนว
- (ออปชัน) จำกัดจำนวนต่อแนวด้วย --max_per_genre
การใช้งาน:
  python merge_import_into_master.py --master MASTER.csv --import IMPORT.csv --out OUT.csv
  python merge_import_into_master.py --master MASTER.csv --import IMPORT.csv --out OUT.csv --max_per_genre 100
"""
import argparse, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--import", dest="import_",
                    required=True, help="CSV to add/merge in")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max_per_genre", type=int, default=0)
    args = ap.parse_args()

    # อ่านไฟล์
    df_m = pd.read_csv(args.master, encoding="utf-8-sig")
    df_i = pd.read_csv(args.import_, encoding="utf-8-sig")

    # รวม + ตัดซ้ำด้วย URL
    df = pd.concat([df_m, df_i], ignore_index=True)
    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"], keep="first")

    # ทำความสะอาดช่อง genre
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.strip()

    # จำกัดจำนวนต่อแนว (ถ้าระบุ)
    if args.max_per_genre and args.max_per_genre > 0:
        df = (df.groupby("genre", group_keys=False)
                .apply(lambda g: g.head(args.max_per_genre))
                .reset_index(drop=True))

    # จัดเรียงและรีเซ็ต index_in_genre ต่อแนว
    order_cols = [c for c in ["genre","index_in_genre","track_title","artist","bpm","duration_sec","license","source","url","notes"] if c in df.columns]
    if order_cols:
        df = df[order_cols]

    df = (df.sort_values(["genre","track_title"], na_position="last")
            .reset_index(drop=True))

    if "index_in_genre" in df.columns:
        df["index_in_genre"] = (
            df.groupby("genre").cumcount() + 1
        )

    # เขียนไฟล์ออก
    df.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"[DONE] wrote {len(df)} rows to {args.out}")

if __name__ == "__main__":
    main()
