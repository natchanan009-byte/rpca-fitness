"""
app.py — ระบบบันทึกและคำนวณคะแนนสมรรถภาพร่างกาย นรต.
เรียกใช้ด้วย:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date

import auth
import database as db
import scoring

# ---------------------------------------------------------------------------
# ตั้งค่าหน้าเว็บ
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ระบบบันทึกคะแนนสมรรถภาพร่างกาย นรต.",
    page_icon="👮",
    layout="wide",
)

db.init_db()

# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

def _init_session():
    defaults = {
        "logged_in":  False,
        "username":   "",
        "active_page": "dashboard",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session()


# ---------------------------------------------------------------------------
# หน้า Login
# ---------------------------------------------------------------------------

def page_login():
    col_c, col_form, col_r = st.columns([1, 2, 1])
    with col_form:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 👮 ระบบบันทึกคะแนนสมรรถภาพร่างกาย นรต.")
        st.markdown("### โรงเรียนนายร้อยตำรวจ")
        st.markdown("---")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="เช่น rpca41")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)

        if submitted:
            if auth.verify_login(username, password):
                st.session_state.logged_in  = True
                st.session_state.username   = username.strip().lower()
                st.session_state.active_page = "dashboard"
                st.rerun()
            else:
                st.error("Username หรือ Password ไม่ถูกต้อง")

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("👤 สำหรับผู้บังคับหมวด / ผู้ช่วยผู้บังคับหมวด เท่านั้น")


# ---------------------------------------------------------------------------
# Sidebar — navigation
# ---------------------------------------------------------------------------

def render_sidebar():
    username     = st.session_state.username
    display_name = auth.get_display_name(username)

    with st.sidebar:
        st.markdown(f"### 👤 {display_name}")
        st.caption(f"เข้าสู่ระบบในฐานะ: `{username}`")
        st.markdown("---")

        menu_items = {
            "dashboard":      "📊 สรุปผลภาพรวม",
            "manage_students": "📋 จัดการข้อมูลนักเรียน",
            "record_test":    "✏️ บันทึกผลทดสอบ",
            "individual":     "🔍 ดูรายบุคคล",
        }
        for page_key, label in menu_items.items():
            if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                st.session_state.active_page = page_key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            for key in ["logged_in", "username", "active_page"]:
                st.session_state[key] = False if key == "logged_in" else ""
            st.rerun()


# ---------------------------------------------------------------------------
# helpers ทั่วไป
# ---------------------------------------------------------------------------

def _user_platoon() -> str | None:
    """คืนหมวดของผู้ใช้ — rpca00 คืน None (ดูได้ทุกหมวด)"""
    username = st.session_state.username
    if auth.is_commander(username):
        return None
    return str(int(username.replace("rpca", "")))  # "rpca01" → "1"


def _score_badge(score: int | None) -> str:
    if score is None:
        return "—"
    color = "#27ae60" if score >= 50 else ("#e67e22" if score >= 25 else "#e74c3c")
    return f'<span style="color:{color};font-weight:bold">{score}</span>'


# ---------------------------------------------------------------------------
# หน้า Dashboard — ตารางสรุปภาพรวม
# ---------------------------------------------------------------------------

def page_dashboard():
    st.title("📊 สรุปผลสมรรถภาพร่างกาย นรต.")
    platoon = _user_platoon()

    # กรองหมวด (เฉพาะ rpca00 เลือกได้)
    if auth.is_commander(st.session_state.username):
        options = ["ทุกหมวด", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        sel = st.selectbox("แสดงผลหมวด", options, index=0)
        platoon = None if sel == "ทุกหมวด" else sel

    rows = db.get_all_latest_results(platoon)
    if not rows:
        st.info("ยังไม่มีข้อมูลนักเรียนในระบบ")
        return

    df = pd.DataFrame(rows)
    df.rename(columns={
        "student_id": "รหัส", "full_name": "ชื่อ-นามสกุล",
        "platoon": "หมวด", "test_date": "วันทดสอบ",
        "total_score": "คะแนนรวม", "percentage": "%",
        "is_passed": "ผล",
        "s1": "ดึงข้อ", "s2": "พุ่งเท้า", "s3": "ดันพื้น",
        "s4": "ลุกนั่ง", "s5": "เชือก", "s6": "วิ่ง", "s7": "ว่ายน้ำ",
    }, inplace=True)

    df["ผล"] = df["ผล"].map(lambda v: "✅ ผ่าน" if v == 1 else ("❌ ไม่ผ่าน" if v == 0 else "—"))
    df["%"] = df["%"].map(lambda v: f"{v:.2f}" if v is not None else "—")

    cols_show = ["รหัส", "ชื่อ-นามสกุล", "หมวด", "วันทดสอบ",
                 "ดึงข้อ", "พุ่งเท้า", "ดันพื้น", "ลุกนั่ง",
                 "เชือก", "วิ่ง", "ว่ายน้ำ",
                 "คะแนนรวม", "%", "ผล"]
    st.dataframe(df[cols_show], use_container_width=True, hide_index=True)

    # สถิติย่อ
    st.markdown("---")
    total_students = len(df)
    passed = (df["ผล"] == "✅ ผ่าน").sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนนักเรียน", total_students)
    col2.metric("ผ่านเกณฑ์", passed)
    col3.metric("ไม่ผ่านเกณฑ์", total_students - passed)


# ---------------------------------------------------------------------------
# หน้าจัดการข้อมูลนักเรียน
# ---------------------------------------------------------------------------

def page_manage_students():
    st.title("📋 จัดการข้อมูลนักเรียน")
    username = st.session_state.username
    platoon  = _user_platoon()

    tab_list, tab_add, tab_edit = st.tabs(["รายชื่อนักเรียน", "เพิ่มนักเรียน", "แก้ไข/ลบนักเรียน"])

    # ── รายชื่อ ───────────────────────────────────────────────
    with tab_list:
        if auth.is_commander(username):
            options = ["ทุกหมวด"] + [str(i) for i in range(1, 10)]
            sel = st.selectbox("กรองตามหมวด", options, key="list_platoon_sel")
            show_platoon = None if sel == "ทุกหมวด" else sel
        else:
            show_platoon = platoon

        students = db.get_students(show_platoon)
        if students:
            df = pd.DataFrame(students)[
                ["student_id", "full_name", "platoon", "weight_kg", "height_cm", "updated_by", "created_at"]
            ]
            df.columns = ["รหัส", "ชื่อ-นามสกุล", "หมวด", "น้ำหนัก(กก.)", "ส่วนสูง(ซม.)", "บันทึกโดย", "วันที่สร้าง"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"จำนวนนักเรียนทั้งหมด: {len(students)} คน")
        else:
            st.info("ยังไม่มีข้อมูลนักเรียน")

    # ── เพิ่มนักเรียน ─────────────────────────────────────────
    with tab_add:
        with st.form("add_student_form"):
            st.markdown("#### เพิ่มนักเรียนใหม่")
            c1, c2 = st.columns(2)
            with c1:
                new_sid  = st.text_input("รหัสนักเรียน *", placeholder="เช่น 6701")
                new_name = st.text_input("ชื่อ-นามสกุล *", placeholder="นรต. ...")
                if auth.is_commander(username):
                    new_platoon = st.selectbox("หมวด *", [str(i) for i in range(1, 10)], key="add_platoon")
                else:
                    new_platoon = platoon
                    st.text_input("หมวด", value=platoon, disabled=True)
            with c2:
                new_weight = st.number_input("น้ำหนัก (กก.)", 30.0, 150.0, 65.0, 0.1)
                new_height = st.number_input("ส่วนสูง (ซม.)", 100.0, 220.0, 170.0, 0.1)

            if st.form_submit_button("บันทึกนักเรียน", use_container_width=True):
                if not new_sid.strip() or not new_name.strip():
                    st.error("กรุณากรอกรหัสนักเรียนและชื่อ-นามสกุล")
                else:
                    ok = db.add_student(
                        new_sid.strip(), new_name.strip(),
                        new_platoon, new_weight, new_height, username,
                    )
                    if ok:
                        st.success(f"เพิ่มนักเรียน {new_name} สำเร็จ")
                    else:
                        st.error(f"รหัสนักเรียน {new_sid} มีอยู่แล้วในระบบ")

    # ── แก้ไข/ลบ ───────────────────────────────────────────────
    with tab_edit:
        students_edit = db.get_students(platoon)
        if not students_edit:
            st.info("ยังไม่มีข้อมูลนักเรียนในหมวดนี้")
            return

        options_edit = {f"{s['student_id']} — {s['full_name']}": s["student_id"] for s in students_edit}
        sel_key = st.selectbox("เลือกนักเรียน", list(options_edit.keys()), key="edit_sel")
        sel_sid = options_edit[sel_key]
        stu = db.get_student(sel_sid)

        if stu:
            with st.form("edit_student_form"):
                c1, c2 = st.columns(2)
                with c1:
                    e_name   = st.text_input("ชื่อ-นามสกุล", stu["full_name"])
                    if auth.is_commander(username):
                        e_platoon = st.selectbox(
                            "หมวด", [str(i) for i in range(1, 10)],
                            index=[str(i) for i in range(1, 10)].index(stu["platoon"]),
                            key="edit_platoon",
                        )
                    else:
                        e_platoon = stu["platoon"]
                        st.text_input("หมวด", value=stu["platoon"], disabled=True)
                with c2:
                    e_weight = st.number_input("น้ำหนัก (กก.)", 30.0, 150.0,
                                               float(stu["weight_kg"] or 65), 0.1)
                    e_height = st.number_input("ส่วนสูง (ซม.)", 100.0, 220.0,
                                               float(stu["height_cm"] or 170), 0.1)

                col_save, col_del = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 บันทึกการแก้ไข", use_container_width=True):
                        db.update_student(sel_sid, e_name, e_platoon,
                                          e_weight, e_height, username)
                        st.success("อัปเดตข้อมูลสำเร็จ")
                        st.rerun()
                with col_del:
                    if st.form_submit_button("🗑️ ลบนักเรียน", use_container_width=True):
                        db.delete_student(sel_sid)
                        st.warning(f"ลบ {stu['full_name']} ออกจากระบบแล้ว")
                        st.rerun()


# ---------------------------------------------------------------------------
# หน้าบันทึกผลทดสอบ
# ---------------------------------------------------------------------------

def page_record_test():
    st.title("✏️ บันทึกผลทดสอบสมรรถภาพร่างกาย")
    username = st.session_state.username
    platoon  = _user_platoon()

    students = db.get_students(platoon)
    if not students:
        st.warning("ยังไม่มีนักเรียนในระบบ กรุณาเพิ่มนักเรียนก่อน")
        return

    options = {f"{s['student_id']} — {s['full_name']}": s["student_id"] for s in students}
    sel_key = st.selectbox("เลือกนักเรียน", list(options.keys()))
    sel_sid = options[sel_key]
    stu     = db.get_student(sel_sid)

    # BMI
    weight_kg = float(stu["weight_kg"] or 65)
    height_cm = float(stu["height_cm"] or 170)
    height_m  = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)

    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    col_info1.metric("ชื่อ-นามสกุล", stu["full_name"])
    col_info2.metric("น้ำหนัก (กก.)", f"{weight_kg:.1f}")
    col_info3.metric("ส่วนสูง (ซม.)", f"{height_cm:.1f}")
    with col_info4:
        st.metric("ค่า BMI", f"{bmi:.2f}")
        if bmi < 18.5:
            st.warning("น้ำหนักน้อยกว่าเกณฑ์")
        elif bmi < 23.0:
            st.success("น้ำหนักปกติ")
        elif bmi < 25.0:
            st.info("น้ำหนักเกิน (ท้วม)")
        else:
            st.error("โรคอ้วน")

    st.markdown("---")

    # โหลดข้อมูลล่าสุดมาเป็นค่า default
    last = db.get_latest_result(sel_sid)

    with st.form("record_test_form"):
        st.markdown("### 📅 วันที่ทดสอบ")
        test_date = st.date_input("วันที่ทดสอบ", value=date.today())

        st.markdown("### 🏃 ผลการทดสอบรายสถานี")
        col_l, col_r = st.columns(2)

        with col_l:
            pullups = st.number_input(
                "1. ดึงข้อราวเดี่ยว (ครั้ง)", 0, 50,
                int(last["pullups"]) if last else 0,
            )
            squat_thrust = st.number_input(
                "2. พุ่งเท้าหลัง / 1 นาที (ครั้ง)", 0, 100,
                int(last["squat_thrust"]) if last else 0,
            )
            pushups = st.number_input(
                "3. ดันพื้น (ครั้ง)", 0, 150,
                int(last["pushups"]) if last else 0,
            )
            situps = st.number_input(
                "4. ลุกนั่ง / 2 นาที (ครั้ง)", 0, 150,
                int(last["situps"]) if last else 0,
            )

        with col_r:
            rope = st.number_input(
                "5. ไต่เชือก (ฟุต)", 0, 30,
                int(last["rope_climbing"]) if last else 0,
            )
            run_time = st.text_input(
                "6. วิ่ง 1,600 เมตร (นาที.วินาที เช่น 7.15)",
                value=last["run_time"] if last else "0.00",
            )
            swim_time = st.text_input(
                "7. ว่ายน้ำ 50 เมตร (นาที.วินาที เช่น 1.05)",
                value=last["swim_time"] if last else "0.00",
            )

        submitted = st.form_submit_button("💾 คำนวณและบันทึก", use_container_width=True)

    if submitted:
        result = scoring.calculate_all_scores(
            pullups, squat_thrust, pushups, situps,
            rope, run_time, swim_time,
        )
        raw = {
            "pullups": pullups, "squat_thrust": squat_thrust,
            "pushups": pushups, "situps": situps,
            "rope_climbing": rope, "run_time": run_time, "swim_time": swim_time,
        }
        db.save_test_result(sel_sid, str(test_date), result, raw, username)

        # แสดงผลทันที
        st.markdown("---")
        st.markdown("### 📊 สรุปผลคะแนน")

        stations = [
            ("1. ดึงข้อราวเดี่ยว",      f"{pullups} ครั้ง",     result["s1"]),
            ("2. พุ่งเท้าหลัง (1 นาที)", f"{squat_thrust} ครั้ง", result["s2"]),
            ("3. ดันพื้น",               f"{pushups} ครั้ง",      result["s3"]),
            ("4. ลุกนั่ง (2 นาที)",      f"{situps} ครั้ง",       result["s4"]),
            ("5. ไต่เชือก",              f"{rope} ฟุต",           result["s5"]),
            ("6. วิ่ง 1,600 เมตร",       f"{run_time} นาที",      result["s6"]),
            ("7. ว่ายน้ำ 50 เมตร",       f"{swim_time} นาที",     result["s7"]),
        ]
        result_df = pd.DataFrame(
            [
                {
                    "สถานีทดสอบ": name,
                    "สถิติที่ทำได้": stat,
                    "คะแนน (เต็ม 100)": score,
                    "สถานะ": "✅ ผ่าน" if score >= 50 else "❌ ไม่ผ่าน",
                }
                for name, stat, score in stations
            ]
        )
        st.table(result_df)

        c1, c2 = st.columns(2)
        c1.metric("คะแนนรวม (เต็ม 700)", result["total"])
        c2.metric("เปอร์เซ็นต์รวม", f"{result['percentage']:.2f} %")

        if result["is_passed"]:
            st.success(f"🎉 ผ่านเกณฑ์การประเมิน — คะแนนรวม {result['total']} คะแนน")
        else:
            st.error("❌ ไม่ผ่านเกณฑ์ (มีสถานีที่คะแนนต่ำกว่าเกณฑ์ หรือคะแนนรวมไม่ถึง 420)")


# ---------------------------------------------------------------------------
# หน้าดูผลรายบุคคล
# ---------------------------------------------------------------------------

def page_individual():
    st.title("🔍 ดูผลการทดสอบรายบุคคล")
    platoon  = _user_platoon()
    students = db.get_students(platoon)

    if not students:
        st.info("ยังไม่มีข้อมูลนักเรียน")
        return

    options = {f"{s['student_id']} — {s['full_name']}": s["student_id"] for s in students}
    sel_key = st.selectbox("เลือกนักเรียน", list(options.keys()))
    sel_sid = options[sel_key]
    stu     = db.get_student(sel_sid)

    # ข้อมูลนักเรียน
    weight_kg = float(stu["weight_kg"] or 65)
    height_cm = float(stu["height_cm"] or 170)
    bmi = weight_kg / (height_cm / 100) ** 2

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ชื่อ-นามสกุล", stu["full_name"])
    c2.metric("น้ำหนัก (กก.)", f"{weight_kg:.1f}")
    c3.metric("ส่วนสูง (ซม.)", f"{height_cm:.1f}")
    c4.metric("BMI", f"{bmi:.2f}")
    st.markdown("---")

    # ประวัติผลทดสอบ
    results = db.get_test_results(sel_sid)
    if not results:
        st.info("ยังไม่มีผลการทดสอบสำหรับนักเรียนคนนี้")
        return

    st.markdown(f"### ประวัติผลทดสอบ ({len(results)} ครั้ง)")

    df_hist = pd.DataFrame(results)[[
        "test_date", "s1", "s2", "s3", "s4", "s5", "s6", "s7",
        "total_score", "percentage", "is_passed", "recorded_by",
    ]]
    df_hist.columns = [
        "วันทดสอบ", "ดึงข้อ", "พุ่งเท้า", "ดันพื้น", "ลุกนั่ง",
        "เชือก", "วิ่ง", "ว่ายน้ำ",
        "รวม", "%", "ผล", "บันทึกโดย",
    ]
    df_hist["ผล"] = df_hist["ผล"].map(lambda v: "✅ ผ่าน" if v == 1 else "❌ ไม่ผ่าน")
    df_hist["%"]  = df_hist["%"].map(lambda v: f"{v:.2f}" if v else "—")
    st.dataframe(df_hist, use_container_width=True, hide_index=True)

    # แสดงผลล่าสุดแบบละเอียด
    st.markdown("---")
    st.markdown("### รายละเอียดผลล่าสุด")
    latest = results[0]

    station_names = [
        "1. ดึงข้อราวเดี่ยว", "2. พุ่งเท้าหลัง (1 นาที)",
        "3. ดันพื้น", "4. ลุกนั่ง (2 นาที)",
        "5. ไต่เชือก", "6. วิ่ง 1,600 เมตร", "7. ว่ายน้ำ 50 เมตร",
    ]
    raw_vals = [
        f"{latest['pullups']} ครั้ง",
        f"{latest['squat_thrust']} ครั้ง",
        f"{latest['pushups']} ครั้ง",
        f"{latest['situps']} ครั้ง",
        f"{latest['rope_climbing']} ฟุต",
        f"{latest['run_time']} นาที",
        f"{latest['swim_time']} นาที",
    ]
    scores_latest = [
        latest["s1"], latest["s2"], latest["s3"], latest["s4"],
        latest["s5"], latest["s6"], latest["s7"],
    ]
    detail_df = pd.DataFrame({
        "สถานี":        station_names,
        "สถิติ":        raw_vals,
        "คะแนน":       scores_latest,
        "สถานะ":       ["✅ ผ่าน" if s >= 50 else "❌ ไม่ผ่าน" for s in scores_latest],
    })
    st.table(detail_df)

    c_tot, c_pct = st.columns(2)
    c_tot.metric("คะแนนรวม (เต็ม 700)", latest["total_score"])
    c_pct.metric("เปอร์เซ็นต์", f"{latest['percentage']:.2f} %")

    if latest["is_passed"]:
        st.success(f"🎉 ผ่านเกณฑ์ — คะแนนรวม {latest['total_score']} คะแนน")
    else:
        st.error("❌ ไม่ผ่านเกณฑ์")


# ---------------------------------------------------------------------------
# Main — routing
# ---------------------------------------------------------------------------

def main():
    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    page = st.session_state.active_page
    if page == "dashboard":
        page_dashboard()
    elif page == "manage_students":
        page_manage_students()
    elif page == "record_test":
        page_record_test()
    elif page == "individual":
        page_individual()
    else:
        page_dashboard()


if __name__ == "__main__" or True:
    main()

