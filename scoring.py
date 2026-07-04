"""
scoring.py — ฟังก์ชันคำนวณคะแนนสมรรถภาพร่างกาย 7 สถานี
"""


def get_pullups_score(count: int) -> int:
    """ดึงข้อราวเดี่ยว"""
    table = {
        20: 100, 19: 98, 18: 96, 17: 93, 16: 90,
        15: 90,  14: 87, 13: 83, 12: 74, 11: 69,
        10: 63,   9: 58,  8: 52,  7: 46,  6: 40,
         5: 33,   4: 26,
    }
    count = int(count)
    if count >= 20:
        return 100
    if count < 4:
        return 0
    return table.get(count, 0)


def get_squat_thrust_score(count: int) -> int:
    """พุ่งเท้าหลัง 1 นาที"""
    table = {
        41: 100, 40: 98, 39: 93, 38: 89, 37: 85,
        36: 80,  35: 76, 34: 72, 33: 67, 32: 63,
        31: 59,  30: 55, 29: 51, 28: 47, 27: 43,
        26: 40,  25: 36, 24: 32, 23: 28, 22: 25,
        21: 22,
    }
    count = int(count)
    if count >= 41:
        return 100
    if count < 21:
        return 0
    return table.get(count, 0)


def get_pushups_score(count: int) -> int:
    """ดันพื้น"""
    count = int(count)
    if count >= 54:
        return 100
    if count <= 9:
        return 0
    table = {
        54: 100, 53: 95, 52: 90, 51: 85, 50: 80,
        49: 78,  48: 76, 47: 74, 46: 72, 45: 70,
        44: 68,  43: 66, 42: 65, 41: 64, 40: 63,
        39: 62,  38: 61, 37: 60, 36: 59, 35: 58,
        34: 57,  33: 56, 32: 55, 31: 54, 30: 53,
        29: 52,  28: 51, 27: 50, 26: 49, 25: 48,
        24: 47,  23: 46, 22: 45, 21: 44, 20: 43,
        19: 42,  18: 41, 17: 40, 16: 38, 15: 36,
        14: 34,  13: 32, 12: 30, 11: 28, 10: 26,
         9: 24,
    }
    return table.get(count, 0)


def get_situps_score(count: int) -> int:
    """ลุกนั่ง 2 นาที"""
    count = int(count)
    if count >= 79:
        return 100
    if count < 13:
        return 0
    table = {
        79: 100, 78: 97, 77: 94, 76: 92, 75: 90,
        74: 88,  73: 86, 72: 84, 71: 82, 70: 80,
        69: 78,  68: 76, 67: 75, 66: 74, 65: 73,
        64: 72,  63: 71, 62: 70, 61: 69, 60: 68,
        59: 67,  58: 66, 57: 65, 56: 64, 55: 63,
        54: 62,  53: 61, 52: 60, 51: 59, 50: 58,
        49: 57,  48: 56, 47: 55, 46: 54, 45: 53,
        44: 52,  43: 51, 42: 50, 41: 49, 40: 48,
        39: 47,  38: 46, 37: 45, 36: 44, 35: 43,
        34: 42,  33: 41, 32: 40, 31: 39, 30: 38,
        29: 37,  28: 36, 27: 35, 26: 34, 25: 33,
        24: 32,  23: 31, 22: 30, 21: 29, 20: 28,
        19: 27,  18: 26, 17: 25, 16: 24, 15: 23,
        14: 22,  13: 21,
    }
    return table.get(count, 0)


def get_rope_climbing_score(feet: int) -> int:
    """ไต่เชือก"""
    table = {
        20: 100, 19: 95, 18: 90, 17: 86, 16: 82,
        15: 78,  14: 74, 13: 71, 12: 68, 11: 65,
        10: 62,   9: 59,  8: 56,  7: 53,  6: 50,
         5: 41,   4: 33,  3: 23,
    }
    feet = int(feet)
    if feet >= 20:
        return 100
    if feet < 3:
        return 0
    return table.get(feet, 0)


def get_running_score(time_str: str) -> int:
    """วิ่ง 1,600 เมตร  รับค่าเป็น นาที.วินาที เช่น 7.15"""
    try:
        t = float(time_str)
    except (ValueError, TypeError):
        return 0
    if t <= 6.00:
        return 100
    if t > 11.12:
        return 0
    if t <= 6.06:   return 98
    if t <= 6.12:   return 96
    if t <= 6.18:   return 94
    if t <= 6.24:   return 91
    if t <= 6.30:   return 88
    if t <= 6.36:   return 85
    if t <= 6.42:   return 82
    if t <= 6.48:   return 80
    if t <= 6.54:   return 78
    if t <= 7.00:   return 76
    if t <= 7.06:   return 74
    if t <= 7.12:   return 72
    if t <= 7.18:   return 70
    if t <= 7.24:   return 68
    if t <= 7.30:   return 66
    if t <= 7.36:   return 64
    if t <= 7.42:   return 62
    if t <= 7.48:   return 60
    if t <= 7.54:   return 58
    if t <= 8.00:   return 56
    if t <= 8.30:   return 50
    if t <= 9.00:   return 45
    if t <= 9.30:   return 40
    if t <= 10.00:  return 35
    if t <= 10.30:  return 30
    if t <= 11.00:  return 23
    return 21


def get_swimming_score(time_str: str) -> int:
    """ว่ายน้ำ 50 เมตร  รับค่าเป็น นาที.วินาที เช่น 1.05"""
    try:
        t = round(float(time_str), 2)
    except (ValueError, TypeError):
        return 0
    if t <= 1.00:
        return 100
    if t >= 1.12:
        return 25
    table = {
        1.01: 92, 1.02: 85, 1.03: 78, 1.04: 71,
        1.05: 65, 1.06: 59, 1.07: 53, 1.08: 47,
        1.09: 41, 1.10: 35, 1.11: 30,
    }
    return table.get(t, 25)


def calculate_all_scores(
    pullups, squat_thrust, pushups, situps,
    rope, run_time, swim_time
) -> dict:
    """คำนวณคะแนนทั้ง 7 สถานีและสรุปผล"""
    s1 = get_pullups_score(pullups)
    s2 = get_squat_thrust_score(squat_thrust)
    s3 = get_pushups_score(pushups)
    s4 = get_situps_score(situps)
    s5 = get_rope_climbing_score(rope)
    s6 = get_running_score(run_time)
    s7 = get_swimming_score(swim_time)

    scores = [s1, s2, s3, s4, s5, s6, s7]
    total = sum(scores)
    percentage = (total / 700) * 100

    passed_all_50 = all(s >= 50 for s in scores)
    passed_total  = all(s >= 25 for s in scores) and total >= 420
    is_passed     = passed_all_50 or passed_total

    return {
        "s1": s1, "s2": s2, "s3": s3, "s4": s4,
        "s5": s5, "s6": s6, "s7": s7,
        "total": total,
        "percentage": round(percentage, 2),
        "is_passed": is_passed,
    }
