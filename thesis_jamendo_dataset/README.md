# Exercise Music Dataset from Jamendo

โปรเจกต์นี้ใช้ดึงเพลงจาก Jamendo (16 แนวเพลง × 100 เพลง) และคำนวณค่า BPM จากไฟล์เสียง  
ผลลัพธ์หลักคือไฟล์ `jamendo_with_bpm.csv` สำหรับใช้ทำงานวิจัย/แอปแนะนำเพลงออกกำลังกาย

---

## 1. สภาพแวดล้อม (Environment)

- แนะนำ Python: **3.11**
- ไม่ต้องใช้ env เดิมของผู้พัฒนา สามารถสร้าง env ใหม่เองได้

ตัวอย่างใช้ **conda**:

```bash
conda create -n jamscrape python=3.11 -y
conda activate jamscrape


pip install requests numpy librosa soundfile pandas




## 2. ไฟล์สำคัญในโฟลเดอร์นี้
สคริปต์หลัก
fetch_jamendo_16genres_search.py
ดึงเพลงจาก Jamendo 16 แนวเพลง โดยใช้ Jamendo API
กรองเฉพาะเพลงที่มีลิขสิทธิ์แบบ CC BY / CC BY-SA / CC0 (ใช้เชิงพาณิชย์ได้)

merge_import_into_master.py
รวมไฟล์เพลงจากหลายไฟล์ และจำกัดจำนวนไม่เกิน 100 เพลงต่อแนว

estimate_bpm_from_page.py
อ่านไฟล์ CSV, หา track id/ลิงก์เสียงจากหน้า Jamendo, ดาวน์โหลดเสียงช่วงสั้น ๆ
แล้วใช้ librosa คำนวณ BPM จากสัญญาณเสียง

ไฟล์ข้อมูล (CSV)
1.jamendo_16genres_cc.csv
เพลง 16 แนวที่ดึงจาก Jamendo ด้วย API (เวอร์ชันหลัก)
2.jamendo_missing_pop_gospel.csv
เพลงเสริม (เช่น Pop / Gospel) ที่ดึงเพิ่มเมื่อแนวใดแนวหนึ่งยังไม่ถึง 100 เพลง
3.jamendo_16genres_cc_merged.csv
ไฟล์รวมก่อนจำกัด 100 เพลงต่อแนว (อาจใช้เป็นข้อมูลประกอบ)
4.jamendo_16genres_cc_FULL_keepldups.csv
ไฟล์รวมที่ผ่านการจำกัด 100 เพลงต่อแนว เรียบร้อยแล้ว (16 แนว = 1600 เพลง)
ใช้เป็นอินพุตให้สคริปต์คำนวณ BPM
5.jamendo_with_bpm.csv
ไฟล์ผลลัพธ์สุดท้าย มีคอลัมน์ bpm เพิ่มเข้ามา
ใช้เป็น Dataset หลักในงานวิจัย


## 3. การใช้ Jamendo API
ในการใช้งานต้องมี client_id ของตนเองจาก Jamendo Developer:
สมัครที่ Jamendo Developer
สร้าง Application ใหม่
จดค่า client_id ไว้ใช้กับสคริปต์ (เช่น 1b2b3b4b)
ไฟล์สคริปต์จะอ่าน client_id จาก argument ผ่านบรรทัดคำสั่ง

## 4. ขั้นตอนการสร้าง Dataset (ตั้งแต่ต้นจนได้ jamendo_with_bpm.csv)
Step 1: ดึงเพลงจาก Jamendo (16 แนว)
conda activate jamscrape   # หรือ env ที่สร้างไว้
python fetch_jamendo_16genres_search.py --client_id YOUR_CLIENT_ID
ถ้ามีแนวที่ยังขาด จะดึงเพิ่มไปไว้ในไฟล์เสริม เช่น jamendo_missing_pop_gospel.csv) เเล้วใช้ query เเค่ 2 genre


Step 2: รวมไฟล์ + จำกัด 100 เพลงต่อแนว
ตัวอย่างคำสั่ง (Windows CMD): //terminal 
python merge_import_into_master.py ^
  --master "jamendo_16genres_cc.csv" ^
  --import "jamendo_missing_pop_gospel.csv" ^
  --out "jamendo_16genres_cc_FULL_keepldups.csv" ^
  --max_per_genre 100

Step 3: คำนวณ BPM จากไฟล์เสียง
python estimate_bpm_from_page.py ^
  --client_id YOUR_CLIENT_ID ^
  --search_client_id YOUR_CLIENT_ID ^
  --in "jamendo_16genres_cc_FULL_keepldups.csv" ^
  --out "jamendo_with_bpm.csv" ^
  --max_rows 1600 ^
  --duration 30 ^
  --verbose

สคริปต์จะ:
อ่านแถวใน CSV ที่ bpm ยังว่าง
หา track id จาก url หรือค้นด้วย search (ชื่อเพลง + ศิลปิน)
ดึงลิงก์เสียงจาก Jamendo
ดาวน์โหลดช่วงเสียงประมาณ 30 วินาที (เป็นไฟล์ชั่วคราว)
ใช้ librosa.beat.tempo คำนวณค่า BPM
เขียนค่า bpm กลับลงไฟล์ jamendo_with_bpm.csv
