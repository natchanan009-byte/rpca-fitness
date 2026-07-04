"""
auth.py — ระบบ authentication สำหรับผู้บังคับหมวดและผู้ช่วยผู้บังคับหมวด
"""

import hashlib
import hmac

# รหัสผ่านเดียวกันทุก username
_PASSWORD = "rpca6480"

# รายชื่อ username ที่ได้รับอนุญาต
VALID_USERNAMES: list[str] = [
    "rpca00",
    "rpca41", "rpca42", "rpca43", "rpca44", "rpca45",
    "rpca46", "rpca47", "rpca48", "rpca49",
]

# ป้ายชื่อแสดงผลของแต่ละ username
USERNAME_LABELS: dict[str, str] = {
    "rpca00": "ผู้บังคับหมวด (00)",
    "rpca41": "ผู้ช่วยผู้บังคับหมวด หมู่ 41",
    "rpca42": "ผู้ช่วยผู้บังคับหมวด หมู่ 42",
    "rpca43": "ผู้ช่วยผู้บังคับหมวด หมู่ 43",
    "rpca44": "ผู้ช่วยผู้บังคับหมวด หมู่ 44",
    "rpca45": "ผู้ช่วยผู้บังคับหมวด หมู่ 45",
    "rpca46": "ผู้ช่วยผู้บังคับหมวด หมู่ 46",
    "rpca47": "ผู้ช่วยผู้บังคับหมวด หมู่ 47",
    "rpca48": "ผู้ช่วยผู้บังคับหมวด หมู่ 48",
    "rpca49": "ผู้ช่วยผู้บังคับหมวด หมู่ 49",
}


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# เก็บ hash ของรหัสผ่านที่ถูกต้องไว้เปรียบเทียบ (ไม่เก็บ plain-text)
_HASHED_PASSWORD = _hash(_PASSWORD)


def verify_login(username: str, password: str) -> bool:
    """ตรวจสอบ username / password — คืนค่า True หากถูกต้อง"""
    username = username.strip().lower()
    if username not in VALID_USERNAMES:
        return False
    # เปรียบเทียบ hash เพื่อป้องกัน timing attack
    return hmac.compare_digest(_hash(password), _HASHED_PASSWORD)


def get_display_name(username: str) -> str:
    """คืนชื่อแสดงผลของ username"""
    return USERNAME_LABELS.get(username.strip().lower(), username)


def is_commander(username: str) -> bool:
    """ตรวจสอบว่าเป็นผู้บังคับหมวด (rpca00) หรือไม่"""
    return username.strip().lower() == "rpca00"
