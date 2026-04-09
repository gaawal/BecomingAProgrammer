from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Dict, List

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_LOCK = Lock()

USERS: Dict[str, dict] = {
    "u1001": {
        "id": "u1001",
        "employee_id": "EMP1001",
        "name": "张晨",
        "department": "平台研发",
        "title": "中级工程师",
        "track": "后端",
        "points": 320,
        "level": 2,
        "partner": {
            "name": "ByteBuddy",
            "skin": "debug-orange",
            "status": "busy",
        },
        "tech_tree": ["python", "flask"],
        "achievements": ["bug_hunter"],
    }
}

TASKS: List[dict] = [
    {
        "id": "T-100",
        "title": "修复支付回调幂等性问题",
        "type": "bug_fix",
        "difficulty": 3,
        "project": "支付中台",
        "status": "todo",
        "owner_id": "u1001",
        "base_points": 50,
        "deadline": "2026-04-15",
    },
    {
        "id": "T-101",
        "title": "实现订单列表筛选组件",
        "type": "feature",
        "difficulty": 2,
        "project": "商家控制台",
        "status": "in_progress",
        "owner_id": "u1001",
        "base_points": 35,
        "deadline": "2026-04-12",
    },
]

TEAMS: Dict[str, dict] = {
    "team-a": {
        "id": "team-a",
        "name": "银河突击队",
        "member_ids": ["u1001"],
        "points": 780,
        "rank": 2,
        "unlocked": ["协作冲刺", "零故障周"],
    }
}

REWARDS: List[dict] = [
    {"id": "R-01", "name": "技术书籍券", "cost": 120, "stock": 10},
    {"id": "R-02", "name": "机械键盘基金", "cost": 500, "stock": 3},
]

POINT_LOGS: List[dict] = []

LEVEL_THRESHOLDS = {
    1: 0,
    2: 200,
    3: 500,
    4: 900,
}


def calc_task_points(task: dict, efficiency: float = 1.0) -> int:
    return int(task["base_points"] * task["difficulty"] * efficiency)


def derive_level(points: int) -> int:
    lv = 1
    for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
        if points >= threshold:
            lv = level
    return lv


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "ts": datetime.utcnow().isoformat()})


@app.get("/api/users/<user_id>")
def get_user(user_id: str):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user)


@app.get("/api/tasks")
def list_tasks():
    user_id = request.args.get("user_id")
    status = request.args.get("status")

    rows = TASKS
    if user_id:
        rows = [t for t in rows if t["owner_id"] == user_id]
    if status:
        rows = [t for t in rows if t["status"] == status]

    return jsonify(rows)


@app.post("/api/tasks/<task_id>/complete")
def complete_task(task_id: str):
    payload = request.get_json(silent=True) or {}
    reviewer_passed = payload.get("reviewer_passed", True)
    efficiency = float(payload.get("efficiency", 1.0))

    with DATA_LOCK:
        task = next((t for t in TASKS if t["id"] == task_id), None)
        if not task:
            return jsonify({"message": "Task not found"}), 404
        if task["status"] == "done":
            return jsonify({"message": "Task already completed"}), 409
        if not reviewer_passed:
            task["status"] = "rejected"
            return jsonify({"message": "Review failed, task rejected", "task": task}), 400

        task["status"] = "done"
        points = calc_task_points(task, efficiency=max(0.7, min(1.3, efficiency)))

        user = USERS.get(task["owner_id"])
        if not user:
            return jsonify({"message": "Task owner not found"}), 500

        old_level = user["level"]
        user["points"] += points
        user["level"] = derive_level(user["points"])
        user["partner"]["status"] = "upgrading" if user["level"] > old_level else "idle"

        POINT_LOGS.append(
            {
                "user_id": user["id"],
                "task_id": task["id"],
                "delta": points,
                "reason": "task_complete",
                "at": datetime.utcnow().isoformat(),
            }
        )

    return jsonify(
        {
            "message": "Task completed and points granted",
            "task": task,
            "user": user,
            "points_delta": points,
            "level_up": user["level"] > old_level,
        }
    )


@app.get("/api/teams/<team_id>")
def get_team(team_id: str):
    team = TEAMS.get(team_id)
    if not team:
        return jsonify({"message": "Team not found"}), 404

    members = [USERS[m] for m in team["member_ids"] if m in USERS]
    response = {**team, "members": members}
    return jsonify(response)


@app.get("/api/rewards")
def list_rewards():
    return jsonify(REWARDS)


@app.post("/api/rewards/redeem")
def redeem_reward():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    reward_id = payload.get("reward_id")

    with DATA_LOCK:
        user = USERS.get(user_id)
        reward = next((r for r in REWARDS if r["id"] == reward_id), None)

        if not user:
            return jsonify({"message": "User not found"}), 404
        if not reward:
            return jsonify({"message": "Reward not found"}), 404
        if reward["stock"] <= 0:
            return jsonify({"message": "Reward out of stock"}), 409
        if user["points"] < reward["cost"]:
            return jsonify({"message": "Insufficient points"}), 400

        user["points"] -= reward["cost"]
        reward["stock"] -= 1
        user["level"] = derive_level(user["points"])

        POINT_LOGS.append(
            {
                "user_id": user["id"],
                "reward_id": reward["id"],
                "delta": -reward["cost"],
                "reason": "reward_redeem",
                "at": datetime.utcnow().isoformat(),
            }
        )

    return jsonify({"message": "Redeem success", "user": user, "reward": reward})


@app.get("/api/points/logs")
def list_point_logs():
    user_id = request.args.get("user_id")
    rows = POINT_LOGS
    if user_id:
        rows = [r for r in rows if r["user_id"] == user_id]
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
