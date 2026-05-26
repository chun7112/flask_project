from flask import Flask
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello Flask!"

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 🔥 Render會用PORT
    app.run(host="0.0.0.0", port=port)