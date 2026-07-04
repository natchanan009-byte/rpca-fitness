# 👮 ระบบบันทึกคะแนนสมรรถภาพร่างกาย นรต.

เว็บแอปพลิเคชัน Streamlit สำหรับบันทึกและคำนวณคะแนนสมรรถภาพร่างกายของนักเรียนนายร้อยตำรวจ (7 สถานี)

---

## โครงสร้างไฟล์

```
rpca_fitness/
├── app.py              ← ไฟล์หลัก (Streamlit)
├── auth.py             ← ระบบ Login
├── database.py         ← ฐานข้อมูล (SQLite / PostgreSQL)
├── scoring.py          ← คำนวณคะแนน 7 สถานี
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── secrets.toml.example  ← ตัวอย่างการตั้งค่า
```

---

## รัน Local (ทดสอบในเครื่อง)

```bash
cd rpca_fitness
pip install -r requirements.txt
streamlit run app.py
```

เปิดเบราว์เซอร์ที่ `http://localhost:8501`

### บัญชีผู้ใช้

| Username | Password  | ตำแหน่ง                        |
|----------|-----------|-------------------------------|
| rpca00   | rpca6480  | ผู้บังคับหมวด (ดูได้ทุกหมู่)    |
| rpca41   | rpca6480  | ผู้ช่วยผู้บังคับหมวด หมู่ 41   |
| rpca42–49| rpca6480  | ผู้ช่วยผู้บังคับหมวด หมู่ 42–49|

---

## Deploy ออนไลน์ฟรี (Streamlit Cloud + Supabase)

### ขั้นตอนที่ 1 — สร้างฐานข้อมูลบน Supabase (ฟรี)

1. ไปที่ [https://supabase.com](https://supabase.com) → **Start your project**
2. สร้าง account ด้วย GitHub
3. กด **New Project** → ตั้งชื่อ เช่น `rpca-fitness` → ตั้ง Database Password
4. รอสักครู่ให้โปรเจกต์พร้อม
5. ไปที่ **Settings → Database → Connection string → URI**
6. คัดลอก URI ที่ได้ (รูปแบบ `postgresql://postgres:...@db.xxx.supabase.co:5432/postgres`)

### ขั้นตอนที่ 2 — อัปโหลดโค้ดขึ้น GitHub

1. สมัคร [https://github.com](https://github.com) (ถ้ายังไม่มี)
2. สร้าง repository ใหม่ → ชื่อ `rpca-fitness` → **Private** (ป้องกันรหัสผ่านรั่ว)
3. อัปโหลดไฟล์ทั้งหมดในโฟลเดอร์ `rpca_fitness/` ขึ้น repo (ยกเว้น `secrets.toml`)

### ขั้นตอนที่ 3 — Deploy บน Streamlit Community Cloud (ฟรี)

1. ไปที่ [https://share.streamlit.io](https://share.streamlit.io) → **Sign in with GitHub**
2. กด **New app** → เลือก repo `rpca-fitness` → Main file: `app.py`
3. คลิก **Advanced settings → Secrets** แล้วใส่:

```toml
[database]
url = "postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres"
```

4. กด **Deploy** → รอ 1-2 นาที → เว็บพร้อมใช้งาน!

> เว็บจะได้ URL ประมาณ `https://rpca-fitness-xxxx.streamlit.app`
