import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pet_kanban.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def log_activity(action, target_type, target_id, user="系统", detail=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO activity_logs(action, target_type, target_id, user, detail, created_at) VALUES(?,?,?,?,?,?)",
        (action, target_type, target_id, user, detail, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        role TEXT DEFAULT '',
        avatar_color TEXT DEFAULT '#4A90D9',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS project_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_no TEXT NOT NULL,
        module TEXT DEFAULT '',
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        assignee TEXT DEFAULT '',
        helper TEXT DEFAULT '',
        deadline TEXT DEFAULT '',
        status TEXT DEFAULT '未开始',
        priority TEXT DEFAULT '中',
        progress TEXT DEFAULT '',
        blocker TEXT DEFAULT '',
        next_action TEXT DEFAULT '',
        need_approval INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT DEFAULT '',
        platform TEXT DEFAULT '',
        link TEXT DEFAULT '',
        price REAL DEFAULT 0,
        monthly_sales TEXT DEFAULT '',
        product_type TEXT DEFAULT '',
        selling_points TEXT DEFAULT '',
        pain_points TEXT DEFAULT '',
        our_opportunity TEXT DEFAULT '',
        image_link TEXT DEFAULT '',
        is_key INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS product_requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        req_no TEXT NOT NULL,
        requirement TEXT NOT NULL,
        importance TEXT DEFAULT '中',
        must_have_v1 INTEGER DEFAULT 1,
        description TEXT DEFAULT '',
        final_decision TEXT DEFAULT '',
        owner TEXT DEFAULT '',
        status TEXT DEFAULT '待定'
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_no TEXT NOT NULL,
        product_version TEXT DEFAULT '',
        supplier TEXT DEFAULT '',
        sample_content TEXT DEFAULT '',
        cost REAL DEFAULT 0,
        expected_date TEXT DEFAULT '',
        actual_date TEXT DEFAULT '',
        status TEXT DEFAULT '未打样',
        test_result TEXT DEFAULT '',
        passed INTEGER DEFAULT 0,
        modification_notes TEXT DEFAULT '',
        owner TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT DEFAULT '',
        contact_person TEXT DEFAULT '',
        contact_info TEXT DEFAULT '',
        location TEXT DEFAULT '',
        products TEXT DEFAULT '',
        quote_price TEXT DEFAULT '',
        moq TEXT DEFAULT '',
        sample_cost REAL DEFAULT 0,
        sample_lead_time TEXT DEFAULT '',
        production_lead_time TEXT DEFAULT '',
        advantages TEXT DEFAULT '',
        risks TEXT DEFAULT '',
        cooperation_status TEXT DEFAULT '未联系',
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS cost_profit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_version TEXT NOT NULL,
        chest_harness_cost REAL DEFAULT 0,
        leash_cost REAL DEFAULT 0,
        hardware_cost REAL DEFAULT 0,
        airtag_structure_cost REAL DEFAULT 0,
        customization_cost REAL DEFAULT 0,
        packaging_cost REAL DEFAULT 0,
        labor_cost REAL DEFAULT 0,
        shipping_cost REAL DEFAULT 0,
        other_cost REAL DEFAULT 0,
        total_cost REAL DEFAULT 0,
        suggested_price REAL DEFAULT 0,
        gross_profit REAL DEFAULT 0,
        gross_margin REAL DEFAULT 0,
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT DEFAULT '',
        target_type TEXT DEFAULT '',
        target_id INTEGER DEFAULT 0,
        user TEXT DEFAULT '',
        detail TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    conn.commit()

    # 插入默认数据（仅在表为空时）
    row = c.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] == 0:
        _insert_defaults(c)
        conn.commit()

    conn.close()


def _insert_defaults(c):
    # 用户
    c.execute("INSERT OR IGNORE INTO users(name, role, avatar_color) VALUES(?,?,?)",
              ("阿豪", "项目负责人 / 产品负责人", "#E74C3C"))
    c.execute("INSERT OR IGNORE INTO users(name, role, avatar_color) VALUES(?,?,?)",
              ("潘翔", "财务负责人 / 执行跟进", "#3498DB"))
    c.execute("INSERT OR IGNORE INTO users(name, role, avatar_color) VALUES(?,?,?)",
              ("浩博", "生产负责人 / 供应链负责人", "#2ECC71"))

    # 项目设置
    settings = {
        "project_name": "宠物胸背牵引绳项目",
        "current_phase": "竞品研究",
        "weekly_goal": "完成竞品调研，确认产品核心卖点，启动工厂对接",
    }
    for k, v in settings.items():
        c.execute("INSERT OR IGNORE INTO project_settings(key, value) VALUES(?,?)", (k, v))

    # 默认任务
    tasks = [
        ("T-001", "竞品", "收集20个宠物胸背牵引绳竞品", "在淘宝、京东、亚马逊等平台收集主流竞品", "阿豪", "", "", "进行中", "高", "", "", "", 0),
        ("T-002", "竞品", "收集10个AirTag宠物配件竞品", "重点看AirTag固定方式和用户评价", "阿豪", "", "", "未开始", "高", "", "", "", 0),
        ("T-003", "产品", "整理竞品差评和用户痛点", "汇总各平台差评，提炼核心痛点", "阿豪", "", "", "未开始", "高", "", "", "", 0),
        ("T-004", "产品", "确认第一版产品核心卖点", "基于竞品分析确定差异化卖点", "阿豪", "", "", "未开始", "高", "", "", "", 1),
        ("T-005", "生产", "找3家胸背牵引绳工厂", "优先有宠物用品经验的工厂", "浩博", "", "", "进行中", "高", "", "", "", 0),
        ("T-006", "打样", "找2种AirTag固定结构方案", "嵌入式和外挂式各一种", "浩博", "", "", "未开始", "高", "", "", "", 0),
        ("T-007", "打样", "确认第一版样品结构", "综合成本、工艺、用户体验确定结构", "浩博", "阿豪", "", "未开始", "高", "", "", "", 1),
        ("T-008", "财务", "建立产品成本模板", "建立三个版本的成本核算模板", "潘翔", "", "", "未开始", "高", "", "", "", 0),
        ("T-009", "财务", "整理竞品售价区间", "统计各平台价格分布", "潘翔", "", "", "未开始", "中", "", "", "", 0),
        ("T-010", "供应商", "记录供应商报价", "汇总各供应商报价信息", "潘翔", "浩博", "", "未开始", "高", "", "", "", 0),
        ("T-011", "产品", "确认第一版是否只做3个尺码", "S/M/L 还是更多尺码", "阿豪", "浩博", "", "未开始", "中", "", "", "", 1),
        ("T-012", "产品", "确认是否第一版加入宠物名定制", "评估定制成本和工艺难度", "阿豪", "潘翔", "", "未开始", "高", "", "", "", 1),
        ("T-013", "测试", "找10-20个真实宠物用户试用", "招募测试用户", "阿豪", "潘翔", "", "未开始", "中", "", "", "", 0),
        ("T-014", "测试", "制定样品测试标准", "制定详细的测试清单和通过标准", "浩博", "阿豪", "", "未开始", "高", "", "", "", 0),
        ("T-015", "财务", "计算三个版本毛利", "基础款、定位款、定制款的毛利分析", "潘翔", "", "", "未开始", "高", "", "", "", 0),
    ]
    for t in tasks:
        c.execute("""INSERT INTO tasks(task_no, module, title, description, assignee, helper, deadline,
                     status, priority, progress, blocker, next_action, need_approval) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""", t)

    # 默认产品需求
    reqs = [
        ("R-001", "胸背不勒脖子", "高", 1, "采用加宽加软垫设计，分散压力", "", "阿豪", "待定"),
        ("R-002", "AirTag/定位器固定仓", "高", 1, "专用固定位，防止宠物咬到", "", "阿豪", "待定"),
        ("R-003", "宠物名字定制", "中", 0, "支持刺绣或印字定制宠物名", "", "阿豪", "待定"),
        ("R-004", "快速穿戴", "高", 1, "一秒扣合，快速穿戴设计", "", "阿豪", "待定"),
        ("R-005", "防挣脱", "高", 1, "双重保护结构，防止狗狗挣脱", "", "阿豪", "待定"),
        ("R-006", "不容易被狗咬到定位器", "高", 1, "AirTag安装位设计在狗嘴碰不到的位置", "", "阿豪", "待定"),
        ("R-007", "舒适透气", "中", 1, "透气网面材质，夏天不闷热", "", "阿豪", "待定"),
        ("R-008", "颜色好看", "中", 1, "选择年轻群体喜欢的配色", "", "阿豪", "待定"),
        ("R-009", "尺码清晰", "高", 1, "明确的尺码表和测量指引", "", "阿豪", "待定"),
        ("R-010", "可小批量生产", "高", 1, "工艺支持小批量起订", "", "阿豪", "待定"),
    ]
    for r in reqs:
        c.execute("""INSERT INTO product_requirements(req_no, requirement, importance, must_have_v1,
                     description, final_decision, owner, status) VALUES(?,?,?,?,?,?,?,?)""", r)


# ===================== 任务 CRUD =====================

def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 WHEN '低' THEN 3 END, created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task_by_id(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_task(data):
    conn = get_connection()
    # 自动生成编号
    row = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
    task_no = f"T-{row[0]+1:03d}"
    now = datetime.now().isoformat()
    c = conn.execute("""INSERT INTO tasks(task_no, module, title, description, assignee, helper, deadline,
                 status, priority, progress, blocker, next_action, need_approval, created_at, updated_at)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (task_no, data.get("module",""), data.get("title",""), data.get("description",""),
                  data.get("assignee",""), data.get("helper",""), data.get("deadline",""),
                  data.get("status","未开始"), data.get("priority","中"),
                  data.get("progress",""), data.get("blocker",""), data.get("next_action",""),
                  1 if data.get("need_approval") else 0, now, now))
    conn.commit()
    log_activity("新建任务", "task", c.lastrowid, data.get("assignee","系统"), data.get("title",""))
    conn.close()
    return c.lastrowid


def update_task(task_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["need_approval"] = 1 if data.get("need_approval") else 0
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
    conn.commit()
    log_activity("更新任务", "task", task_id, data.get("assignee","系统"), data.get("title",""))
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    t = conn.execute("SELECT title FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    log_activity("删除任务", "task", task_id, "系统", t["title"] if t else "")
    conn.close()


# ===================== 竞品 CRUD =====================

def get_all_competitors():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM competitors ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_competitor(data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["is_key"] = 1 if data.get("is_key") else 0
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO competitors({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    log_activity("新增竞品", "competitor", c.lastrowid, "阿豪", data.get("name",""))
    conn.close()
    return c.lastrowid


def update_competitor(comp_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["is_key"] = 1 if data.get("is_key") else 0
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [comp_id]
    conn.execute(f"UPDATE competitors SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def delete_competitor(comp_id):
    conn = get_connection()
    conn.execute("DELETE FROM competitors WHERE id=?", (comp_id,))
    conn.commit()
    conn.close()


# ===================== 产品需求 CRUD =====================

def get_all_requirements():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM product_requirements ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_requirement(data):
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM product_requirements").fetchone()
    req_no = f"R-{row[0]+1:03d}"
    data["req_no"] = req_no
    data["must_have_v1"] = 1 if data.get("must_have_v1") else 0
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO product_requirements({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    conn.close()
    return c.lastrowid


def update_requirement(req_id, data):
    conn = get_connection()
    data["must_have_v1"] = 1 if data.get("must_have_v1") else 0
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [req_id]
    conn.execute(f"UPDATE product_requirements SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def delete_requirement(req_id):
    conn = get_connection()
    conn.execute("DELETE FROM product_requirements WHERE id=?", (req_id,))
    conn.commit()
    conn.close()


# ===================== 样品 CRUD =====================

def get_all_samples():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM samples ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_sample(data):
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM samples").fetchone()
    sample_no = f"S-{row[0]+1:03d}"
    data["sample_no"] = sample_no
    data["updated_at"] = datetime.now().isoformat()
    data["passed"] = 1 if data.get("passed") else 0
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO samples({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    log_activity("新增样品", "sample", c.lastrowid, data.get("owner","浩博"), data.get("sample_content",""))
    conn.close()
    return c.lastrowid


def update_sample(sample_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["passed"] = 1 if data.get("passed") else 0
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [sample_id]
    conn.execute(f"UPDATE samples SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def delete_sample(sample_id):
    conn = get_connection()
    conn.execute("DELETE FROM samples WHERE id=?", (sample_id,))
    conn.commit()
    conn.close()


# ===================== 供应商 CRUD =====================

def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_supplier(data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO suppliers({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    log_activity("新增供应商", "supplier", c.lastrowid, "浩博", data.get("name",""))
    conn.close()
    return c.lastrowid


def update_supplier(sup_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [sup_id]
    conn.execute(f"UPDATE suppliers SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def delete_supplier(sup_id):
    conn = get_connection()
    conn.execute("DELETE FROM suppliers WHERE id=?", (sup_id,))
    conn.commit()
    conn.close()


# ===================== 成本利润 CRUD =====================

def get_all_costs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cost_profit ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_cost(data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    # 自动计算
    data["total_cost"] = sum([
        data.get("chest_harness_cost", 0) or 0,
        data.get("leash_cost", 0) or 0,
        data.get("hardware_cost", 0) or 0,
        data.get("airtag_structure_cost", 0) or 0,
        data.get("customization_cost", 0) or 0,
        data.get("packaging_cost", 0) or 0,
        data.get("labor_cost", 0) or 0,
        data.get("shipping_cost", 0) or 0,
        data.get("other_cost", 0) or 0,
    ])
    price = data.get("suggested_price", 0) or 0
    data["gross_profit"] = round(price - data["total_cost"], 2)
    data["gross_margin"] = round((data["gross_profit"] / price * 100), 2) if price > 0 else 0
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO cost_profit({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    conn.close()
    return c.lastrowid


def update_cost(cost_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["total_cost"] = sum([
        data.get("chest_harness_cost", 0) or 0,
        data.get("leash_cost", 0) or 0,
        data.get("hardware_cost", 0) or 0,
        data.get("airtag_structure_cost", 0) or 0,
        data.get("customization_cost", 0) or 0,
        data.get("packaging_cost", 0) or 0,
        data.get("labor_cost", 0) or 0,
        data.get("shipping_cost", 0) or 0,
        data.get("other_cost", 0) or 0,
    ])
    price = data.get("suggested_price", 0) or 0
    data["gross_profit"] = round(price - data["total_cost"], 2)
    data["gross_margin"] = round((data["gross_profit"] / price * 100), 2) if price > 0 else 0
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [cost_id]
    conn.execute(f"UPDATE cost_profit SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()


def delete_cost(cost_id):
    conn = get_connection()
    conn.execute("DELETE FROM cost_profit WHERE id=?", (cost_id,))
    conn.commit()
    conn.close()


# ===================== 项目设置 =====================

def get_setting(key, default=""):
    conn = get_connection()
    row = conn.execute("SELECT value FROM project_settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO project_settings(key, value, updated_at) VALUES(?,?,?)",
                 (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ===================== 统计 =====================

def get_task_stats():
    conn = get_connection()
    stats = {}
    stats["total"] = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    stats["in_progress"] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='进行中'").fetchone()[0]
    stats["completed"] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='已完成'").fetchone()[0]
    stats["at_risk"] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='有风险'").fetchone()[0]
    stats["not_started"] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='未开始'").fetchone()[0]
    stats["waiting"] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='等待中'").fetchone()[0]
    stats["cancelled"] = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='已取消'").fetchone()[0]
    # 延期任务：截止时间不为空且已过期且未完成
    today = datetime.now().strftime("%Y-%m-%d")
    stats["overdue"] = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE deadline != '' AND deadline < ? AND status NOT IN ('已完成','已取消')",
        (today,)
    ).fetchone()[0]
    conn.close()
    return stats


def get_overdue_tasks():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT * FROM tasks WHERE deadline != '' AND deadline < ? AND status NOT IN ('已完成','已取消') ORDER BY deadline",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_risk_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE status='有风险' ORDER BY deadline").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_approval_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE need_approval=1 AND status NOT IN ('已完成','已取消') ORDER BY created_at").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_logs(limit=10):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
