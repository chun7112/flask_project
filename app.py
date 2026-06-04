from flask import Flask, request
from flask_cors import CORS
from datetime import date, timedelta
import pymysql
import random
import os

app = Flask(__name__)
CORS(app)

# ===== 資料庫連線 =====
def get_db():
    return pymysql.connect(
        host="acela.proxy.rlwy.net",
        port=35686,
        user="root",
        password="FLDApMJvyhFcgrxbbevjGlmKUVoyPasD",
        database="railway",
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def home():
    return "Hello Flask!"
    
@app.route("/db-test")
def db_test():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM checkins")

    result = cursor.fetchone()

    conn.close()

    return {
        "total_checkins": result["total"]
    }
    
@app.route("/checkin", methods=["POST"])
def checkin():

    data = request.json
    user_id = data["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    # 檢查今天是否已打卡
    cursor.execute("""
        SELECT *
        FROM checkins
        WHERE user_id = %s
        AND checkin_date = CURDATE()
    """, (user_id,))

    existing = cursor.fetchone()

    if existing:
        conn.close()

        return {
            "success": False,
            "message": "already checked in"
        }

    # 新增打卡
    cursor.execute("""
        INSERT INTO checkins (
            user_id,
            checkin_date
        )
        VALUES (
            %s,
            CURDATE()
        )
    """, (user_id,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "checkin success"
    }
    
@app.route("/streak/<user_id>")
def get_streak(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT checkin_date
        FROM checkins
        WHERE user_id = %s
        ORDER BY checkin_date ASC
    """, (user_id,))

    records = cursor.fetchall()

    conn.close()

    if not records:
        return {
            "current_streak": 0,
            "best_streak": 0,
            "total_checkins": 0
        }

    dates = [r["checkin_date"] for r in records]

    # ===== 計算最高連續 =====
    best_streak = 1
    current_run = 1

    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            current_run += 1
            best_streak = max(best_streak, current_run)
        else:
            current_run = 1

    # ===== 計算目前連續 =====
    current_streak = 0
    today = date.today()

    date_set = set(dates)

    while today in date_set:
        current_streak += 1
        today -= timedelta(days=1)

    return {
        "current_streak": current_streak,
        "best_streak": best_streak,
        "total_checkins": len(dates)
    }

@app.route("/recommend/<goal>")
def recommend(goal):
    goal = goal.lower()  # 👈 統一小寫

    # 🔥 睡眠類
    if "睡" in goal or "sleep" in goal:
        tasks = ["11點前關燈", "睡前不滑手機", "設定睡覺鬧鐘"]

    # 🔥 運動類
    elif "運動" in goal or "exercise" in goal:
        tasks = ["跑步20分鐘", "做10下伏地挺身", "伸展5分鐘"]

    # 🔥 讀書類
    elif "讀書" in goal or "study" in goal:
        tasks = ["讀書30分鐘", "寫一題練習題", "複習昨天的內容"]

    else:
        tasks = []

    return {"tasks": tasks}


@app.route("/quote")
def quote():
    quotes = [
        "今天做一點，明天更輕鬆",
        "先開始，比完美更重要",
        "慢慢來比較快",
        "今天的你，比昨天更好",
        "做一點就贏過沒做",
        "累了可以休息，但不要放棄",
        "堅持不是硬撐，是習慣",
        "你已經比很多人努力了",
        "小進步也是進步",
        "現在開始永遠不晚"
    ]

    return {"quote": random.choice(quotes)}
    
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "success": False,
            "message": "username and password required"
        }, 400

    conn = get_db()
    cursor = conn.cursor()

    # 檢查帳號是否存在
    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()

        return {
            "success": False,
            "message": "username already exists"
        }

    # 建立新帳號
    cursor.execute(
        """
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        """,
        (username, password)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "register success"
    }
    
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE username=%s AND password=%s
        """,
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        return {
            "success": True,
            "message": "login success"
        }

    return {
        "success": False,
        "message": "invalid username or password"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 🔥 Render會用PORT
    app.run(host="0.0.0.0", port=port)
