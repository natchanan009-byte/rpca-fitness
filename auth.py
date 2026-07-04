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
    "rpca01", "rpca02", "rpca03", "rpca04", "rpca05",
    "rpca06", "rpca07", "rpca08", "rpca09",
]

# ป้ายชื่อแสดงผลของแต่ละ username
USERNAME_LABELS: dict[str, str] = {
    "rpca00": "ผู้บังคับหมวด",
    "rpca01": "ผู้ช่วยผู้บังคับหมวด หมวด 1",
    "rpca02": "ผู้ช่วยผู้บังคับหมวด หมวด 2",
    "rpca03": "ผู้ช่วยผู้บังคับหมวด หมวด 3",
    "rpca04": "ผู้ช่วยผู้บังคับหมวด หมวด 4",
    "rpca05": "ผู้ช่วยผู้บังคับหมวด หมวด 5",
    "rpca06": "ผู้ช่วยผู้บังคับหมวด หมวด 6",
    "rpca07": "ผู้ช่วยผู้บังคับหมวด หมวด 7",
    "rpca08": "ผู้ช่วยผู้บังคับหมวด หมวด 8",
    "rpca09": "ผู้ช่วยผู้บังคับหมวด หมวด 9",
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
