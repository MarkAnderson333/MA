"""
难度模型 v1 + 数据管线骨架
==========================
功能：读入用户参数 + 路线数据 -> 提取特征 -> 套难度公式 -> 输出 CSV

运行方式：python difficulty_model_v1.py
"""

import csv      # csv 库：把结果存成表格文件
import math     # math 库：开根号等数学运算
import random   # random 库：生成随机模拟数据

# ================= 第一部分：用户参数 =================
# 这里先手动填，以后改成程序界面输入
USER = {
    "height": 165,        # 身高（cm）
    "weight": 52,         # 体重（kg）
    "left_strength": 3,   # 左臂力量（1-5）
    "right_strength": 4,  # 右臂力量（1-5）
}


def calc_wingspan(height_cm):
    """臂展 ≈ 身高 × 1.03（文献经验值）"""
    return height_cm * 1.03


# ============ 第二部分：模拟路线数据生成器 ============
# 岩点 = 字典：x横坐标, y纵坐标, size大小(1小/2中/3大), kind类型
# 路线 = 字典：route_id编号, angle仰角度数, holds岩点列表

def generate_route(route_id):
    """随机生成一条模拟路线（5-8 个岩点，从下往上爬）"""
    n = random.randint(5, 8)          # 岩点数量
    angle = random.randint(0, 30)     # 仰角 0-30 度
    holds = []
    y = 10                            # 从底部开始
    for i in range(n):
        y += random.randint(8, 15)    # 每次向上 8-15 个单位
        holds.append({
            "x": random.randint(10, 90),
            "y": min(y, 95),
            "size": random.choice([1, 1, 2, 2, 3]),   # 小点更常见
            "kind": random.choice(["jug", "crimp", "sloper", "pinch"]),
        })
    return {"route_id": route_id, "angle": angle, "holds": holds}


def generate_routes(num):
    """生成 num 条模拟路线"""
    routes = []
    for i in range(num):
        routes.append(generate_route(i + 1))
    return routes


# ============ 第三部分：特征提取 ============

def distance(h1, h2):
    """两个岩点之间的直线距离（欧氏距离公式）"""
    return math.sqrt((h1["x"] - h2["x"]) ** 2 + (h1["y"] - h2["y"]) ** 2)


def extract_features(route, wingspan):
    """从一条路线 + 用户臂展，算出模型要用的 4 个特征"""
    holds = route["holds"]

    # 特征1：平均岩点间距（相邻两点），归一化成"占臂展的比例"
    gaps = []
    for i in range(len(holds) - 1):
        gaps.append(distance(holds[i], holds[i + 1]))
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    gap_ratio = avg_gap / wingspan

    # 特征2：仰角占比（0-30 度 -> 0-0.33）
    angle_ratio = route["angle"] / 90.0

    # 特征3：平均岩点大小（1-3），岩点越小越难 -> 取倒数
    sizes = [h["size"] for h in holds]
    avg_size = sum(sizes) / len(sizes)
    size_factor = 1.0 / avg_size

    # 特征4：偏手性惩罚（左右力量差越大，换手时越容易卡壳）
    strength_gap = abs(USER["left_strength"] - USER["right_strength"])
    strength_avg = (USER["left_strength"] + USER["right_strength"]) / 2.0

    return {
        "gap_ratio": gap_ratio,
        "angle_ratio": angle_ratio,
        "size_factor": size_factor,
        "strength_gap": strength_gap,
        "strength_avg": strength_avg,
    }


# ============ 第四部分：难度模型 v1 ============
# 难度 = w1*间距比 + w2*仰角比 + w3*大小系数 - w4*力量 + w5*偏手性惩罚
# 权重是"初始猜测值"，D2 用三组测试数据来调参

W = {"w1": 3.0, "w2": 2.5, "w3": 1.5, "w4": 2.0, "w5": 0.8}


def compute_difficulty(feat):
    """套公式算难度分"""
    d = (W["w1"] * feat["gap_ratio"]
         + W["w2"] * feat["angle_ratio"]
         + W["w3"] * feat["size_factor"]
         - W["w4"] * (feat["strength_avg"] / 5.0)
         + W["w5"] * feat["strength_gap"])
    return round(d, 2)


# ============ 第五部分：主管线 ============

def run_pipeline(routes):
    """跑完整条数据管线，返回每条路线的结果列表"""
    wingspan = calc_wingspan(USER["height"])
    results = []
    for route in routes:
        feat = extract_features(route, wingspan)
        score = compute_difficulty(feat)
        results.append({
            "route_id": route["route_id"],
            "angle": route["angle"],
            "hold_count": len(route["holds"]),
            "difficulty": score,
        })
    return results


def save_csv(results, filename):
    """把结果列表存成 CSV 表格文件"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"已保存: {filename}")


# ============ 主程序入口 ============
if __name__ == "__main__":
    # 1. 生成 30 条模拟路线
    routes = generate_routes(30)

    # 2. 跑管线
    results = run_pipeline(routes)

    # 3. 打印前 5 条看看
    print("前 5 条路线的难度：")
    for r in results[:5]:
        print(r)

    # 4. 存成 CSV
    save_csv(results, "difficulty_results.csv")

    # 5. 运行结束停留（双击时不闪退，按回车才关窗口）
    input("\n程序跑完了，按回车键退出...")
