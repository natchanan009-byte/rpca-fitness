"""
database.py — รองรับ SQLite (local dev) และ PostgreSQL/Supabase (production)

เมื่อ Streamlit secrets มี [database] url → ใช้ PostgreSQL
ไม่มี → ใช้ SQLite ในเครื่อง
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# ตรวจสอบ mode
# ---------------------------------------------------------------------------

def _detect_postgres() -> bool:
    try:
        import streamlit as st
        return bool(st.secrets.get("database", ).get("url", ""))
    except Exception:
        return False


_PG = _detect_postgres()

# ---------------------------------------------------------------------------
# Connection factory + row helpers
# ---------------------------------------------------------------------------

if _PG:
    import psycopg2
    import psycopg2.extras
    import streamlit as st

    def get_connection():
        return psycopg2.connect(
            st.secrets["database"]["url"],
            cursor_factory=psycopg2.extras.RealDictCursor,
            sslmode="require",
        )

    PH        = "%s"                            # parameter placeholder
    AUTO_ID   = "SERIAL PRIMARY KEY"            # auto-increment id column
    TS_NOW    = "NOW()"                         # current timestamp
    TS_COL    = "TIMESTAMP DEFAULT NOW()"       # column default

else:
    import sqlite3

    _DB_PATH = Path(__file__).parent / "rpca_fitness.db"

    def get_connection():
        conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    PH      = "?"
    AUTO_ID = "INTEGER PRIMARY KEY AUTOINCREMENT"
    TS_NOW  = "datetime('now','localtime')"
    TS_COL  = f"TEXT DEFAULT ({TS_NOW})"


def _rows(cur) -> list[dict]:
    return [dict(r) for r in cur.fetchall()]


def _one(cur) -> dict | None:
    r = cur.fetchone()
    return dict(r) if r else None


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------

def init_db() -> None:
    """สร้างตารางหากยังไม่มี"""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS students (
            id          {AUTO_ID},
            student_id  TEXT UNIQUE NOT NULL,
            full_name   TEXT NOT NULL,
            platoon     TEXT NOT NULL,
            weight_kg   REAL,
            height_cm   REAL,
            created_at  {TS_COL},
            updated_by  TEXT
        )
    """)

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS test_results (
            id            {AUTO_ID},
            student_id    TEXT NOT NULL,
            test_date     TEXT NOT NULL,
            pullups       INTEGER DEFAULT 0,
            squat_thrust  INTEGER DEFAULT 0,
            pushups       INTEGER DEFAULT 0,
            situps        INTEGER DEFAULT 0,
            rope_climbing INTEGER DEFAULT 0,
            run_time      TEXT    DEFAULT '0.00',
            swim_time     TEXT    DEFAULT '0.00',
            s1 INTEGER, s2 INTEGER, s3 INTEGER, s4 INTEGER,
            s5 INTEGER, s6 INTEGER, s7 INTEGER,
            total_score   INTEGER,
            percentage    REAL,
            is_passed     INTEGER,
            recorded_by   TEXT,
            updated_at    {TS_COL}
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------

def add_student(student_id: str, full_name: str, platoon: str,
                weight_kg: float, height_cm: float, updated_by: str) -> bool:
    try:
        conn = get_connection()
        conn.cursor().execute(
            f"""INSERT INTO students
                (student_id, full_name, platoon, weight_kg, height_cm, updated_by)
                VALUES ({PH},{PH},{PH},{PH},{PH},{PH})""",
            (student_id, full_name, platoon, weight_kg, height_cm, updated_by),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_student(student_id: str, full_name: str, platoon: str,
                   weight_kg: float, height_cm: float, updated_by: str) -> None:
    conn = get_connection()
    conn.cursor().execute(
        f"""UPDATE students
            SET full_name={PH}, platoon={PH}, weight_kg={PH},
                height_cm={PH}, updated_by={PH}
            WHERE student_id={PH}""",
        (full_name, platoon, weight_kg, height_cm, updated_by, student_id),
    )
    conn.commit()
    conn.close()


def delete_student(student_id: str) -> None:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(f"DELETE FROM test_results WHERE student_id={PH}", (student_id,))
    cur.execute(f"DELETE FROM students WHERE student_id={PH}",     (student_id,))
    conn.commit()
    conn.close()


def get_students(platoon: str | None = None) -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor()
    if platoon:
        cur.execute(
            f"SELECT * FROM students WHERE platoon={PH} ORDER BY student_id",
            (platoon,),
        )
    else:
        cur.execute("SELECT * FROM students ORDER BY platoon, student_id")
    result = _rows(cur)
    conn.close()
    return result


def get_student(student_id: str) -> dict | None:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(f"SELECT * FROM students WHERE student_id={PH}", (student_id,))
    result = _one(cur)
    conn.close()
    return result


# ---------------------------------------------------------------------------
# Test results
# ---------------------------------------------------------------------------

def save_test_result(student_id: str, test_date: str, scores: dict,
                     raw: dict, recorded_by: str) -> None:
    """บันทึกหรืออัปเดตผลทดสอบของนักเรียนในวันนั้น"""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute(
        f"SELECT id FROM test_results WHERE student_id={PH} AND test_date={PH}",
        (student_id, test_date),
    )
    existing = _one(cur)

    params = (
        raw["pullups"], raw["squat_thrust"], raw["pushups"],
        raw["situps"],  raw["rope_climbing"],
        raw["run_time"], raw["swim_time"],
        scores["s1"], scores["s2"], scores["s3"], scores["s4"],
        scores["s5"], scores["s6"], scores["s7"],
        scores["total"], scores["percentage"],
        int(scores["is_passed"]),
        recorded_by,
    )

    if existing:
        cur.execute(
            f"""UPDATE test_results SET
                pullups={PH}, squat_thrust={PH}, pushups={PH}, situps={PH},
                rope_climbing={PH}, run_time={PH}, swim_time={PH},
                s1={PH}, s2={PH}, s3={PH}, s4={PH},
                s5={PH}, s6={PH}, s7={PH},
                total_score={PH}, percentage={PH}, is_passed={PH},
                recorded_by={PH}
                WHERE student_id={PH} AND test_date={PH}""",
            (*params, student_id, test_date),
        )
    else:
        cur.execute(
            f"""INSERT INTO test_results
                (student_id, test_date,
                 pullups, squat_thrust, pushups, situps, rope_climbing,
                 run_time, swim_time,
                 s1, s2, s3, s4, s5, s6, s7,
                 total_score, percentage, is_passed, recorded_by)
                VALUES ({','.join([PH]*20)})""",
            (student_id, test_date, *params),
        )

    conn.commit()
    conn.close()


def get_test_results(student_id: str) -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        f"SELECT * FROM test_results WHERE student_id={PH} ORDER BY test_date DESC",
        (student_id,),
    )
    result = _rows(cur)
    conn.close()
    return result


def get_latest_result(student_id: str) -> dict | None:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        f"""SELECT * FROM test_results WHERE student_id={PH}
            ORDER BY test_date DESC LIMIT 1""",
        (student_id,),
    )
    result = _one(cur)
    conn.close()
    return result


def get_all_latest_results(platoon: str | None = None) -> list[dict]:
    """ดึงผลล่าสุดของทุกนักเรียน"""
    conn = get_connection()
    cur  = conn.cursor()
    where = f"WHERE s.platoon={PH}" if platoon else ""
    args  = (platoon,) if platoon else ()
    cur.execute(
        f"""
        SELECT s.student_id, s.full_name, s.platoon,
               s.weight_kg,  s.height_cm,
               r.test_date,  r.total_score, r.percentage, r.is_passed,
               r.s1, r.s2, r.s3, r.s4, r.s5, r.s6, r.s7
        FROM   students s
        LEFT JOIN test_results r
               ON r.student_id = s.student_id
              AND r.test_date = (
                  SELECT MAX(test_date) FROM test_results
                  WHERE  student_id = s.student_id
              )
        {where}
        ORDER BY s.platoon, s.student_id
        """,
        args,
    )
    result = _rows(cur)
    conn.close()
    return result
