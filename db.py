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

    # ===== 用户表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        role TEXT DEFAULT '',
        avatar_color TEXT DEFAULT '#4A90D9',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 项目设置表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS project_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 任务表 - 添加 plan_id, spu_id, task_type =====
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_no TEXT NOT NULL,
        plan_id INTEGER DEFAULT 0,
        spu_id INTEGER DEFAULT 0,
        task_type TEXT DEFAULT '',
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

    # ===== 竞品表 - 添加关联字段 =====
    c.execute("""CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER DEFAULT 0,
        spu_id INTEGER DEFAULT 0,
        sku_id INTEGER DEFAULT 0,
        category TEXT DEFAULT '',
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
        material TEXT DEFAULT '',
        sizes TEXT DEFAULT '',
        has_engraving INTEGER DEFAULT 0,
        has_locator INTEGER DEFAULT 0,
        pros TEXT DEFAULT '',
        cons TEXT DEFAULT '',
        user_review_summary TEXT DEFAULT '',
        negative_review_reasons TEXT DEFAULT '',
        qa_content TEXT DEFAULT '',
        借鉴_points TEXT DEFAULT '',
        避坑_points TEXT DEFAULT '',
        image_link TEXT DEFAULT '',
        is_key INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 产品需求表 =====
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

    # ===== 样品表 - 添加关联字段和next_action =====
    c.execute("""CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER DEFAULT 0,
        spu_id INTEGER DEFAULT 0,
        sku_id INTEGER DEFAULT 0,
        sample_no TEXT NOT NULL,
        product_version TEXT DEFAULT '',
        supplier TEXT DEFAULT '',
        sample_content TEXT DEFAULT '',
        cost REAL DEFAULT 0,
        expected_date TEXT DEFAULT '',
        actual_date TEXT DEFAULT '',
        status TEXT DEFAULT '待打样',
        test_result TEXT DEFAULT '',
        passed INTEGER DEFAULT 0,
        modification_notes TEXT DEFAULT '',
        owner TEXT DEFAULT '',
        next_action TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 供应商表 - 添加关联字段和特殊服务支持 =====
    c.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER DEFAULT 0,
        spu_id INTEGER DEFAULT 0,
        sku_id INTEGER DEFAULT 0,
        component_id INTEGER DEFAULT 0,
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
        supports_engraving INTEGER DEFAULT 0,
        supports_logo INTEGER DEFAULT 0,
        supports_locator_parts INTEGER DEFAULT 0,
        advantages TEXT DEFAULT '',
        risks TEXT DEFAULT '',
        cooperation_status TEXT DEFAULT '未联系',
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 成本利润表 - 添加关联字段 =====
    c.execute("""CREATE TABLE IF NOT EXISTS cost_profit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER DEFAULT 0,
        spu_id INTEGER DEFAULT 0,
        sku_id INTEGER DEFAULT 0,
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

    # ===== 活动日志表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT DEFAULT '',
        target_type TEXT DEFAULT '',
        target_id INTEGER DEFAULT 0,
        user TEXT DEFAULT '',
        detail TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 开发计划表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS development_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        status TEXT DEFAULT '进行中',
        owner TEXT DEFAULT '焦蒙豪',
        start_date TEXT DEFAULT '',
        target_date TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== SPU表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS spus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER REFERENCES development_plans(id),
        name TEXT NOT NULL,
        category TEXT DEFAULT '',
        positioning TEXT DEFAULT '',
        target_audience TEXT DEFAULT '',
        selling_points TEXT DEFAULT '',
        stage TEXT DEFAULT '概念',
        owner TEXT DEFAULT '焦蒙豪',
        notes TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== SKU表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS skus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spu_id INTEGER REFERENCES spus(id),
        name TEXT DEFAULT '',
        color TEXT DEFAULT '',
        size TEXT DEFAULT '',
        style TEXT DEFAULT '',
        specification TEXT DEFAULT '',
        has_engraving INTEGER DEFAULT 0,
        has_locator_port INTEGER DEFAULT 0,
        has_locator INTEGER DEFAULT 0,
        estimated_price REAL DEFAULT 0,
        status TEXT DEFAULT '开发中',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 零部件表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_id INTEGER REFERENCES skus(id),
        name TEXT NOT NULL,
        type TEXT DEFAULT '其他',
        quantity REAL DEFAULT 1,
        unit TEXT DEFAULT '个',
        unit_price REAL DEFAULT 0,
        supplier TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    # ===== 成本明细表 =====
    c.execute("""CREATE TABLE IF NOT EXISTS cost_items_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cost_plan_id INTEGER DEFAULT 0,
        plan_id INTEGER DEFAULT 0,
        spu_id INTEGER DEFAULT 0,
        sku_id INTEGER DEFAULT 0,
        name TEXT NOT NULL,
        category TEXT DEFAULT '物料',
        quantity REAL DEFAULT 1,
        unit_price REAL DEFAULT 0,
        subtotal REAL DEFAULT 0,
        source TEXT DEFAULT '手动',
        sort_order INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        updated_at TEXT DEFAULT (datetime('now','localtime'))
    )""")

    conn.commit()

    # 插入默认数据
    row = c.execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] == 0:
        _insert_defaults(c)
        conn.commit()

    conn.close()


def _insert_defaults(c):
    # ===== 用户 - 完整姓名 =====
    c.execute("INSERT OR IGNORE INTO users(name, role, avatar_color) VALUES(?,?,?)",
              ("焦蒙豪", "管理员", "#E74C3C"))
    c.execute("INSERT OR IGNORE INTO users(name, role, avatar_color) VALUES(?,?,?)",
              ("潘翔", "管理员", "#3498DB"))
    c.execute("INSERT OR IGNORE INTO users(name, role, avatar_color) VALUES(?,?,?)",
              ("潘浩博", "管理员", "#2ECC71"))

    # ===== 默认开发计划 =====
    c.execute("""INSERT OR IGNORE INTO development_plans(name, description, status, owner, start_date, target_date)
                 VALUES(?,?,?,?,?,?)""",
              ("宠物胸背牵引绳系列开发", "开发宠物胸背牵引绳系列产品", "进行中", "焦蒙豪", 
               datetime.now().strftime("%Y-%m-%d"), ""))

    plan_row = c.execute("SELECT id FROM development_plans WHERE name='宠物胸背牵引绳系列开发'").fetchone()
    plan_id = plan_row[0] if plan_row else 1

    # ===== SPU示例 =====
    spu_data = [
        ("宠物胸背+牵引绳套装", "胸背牵引", "中高端宠物主", "高品质胸背+牵引绳", "概念"),
        ("宠物定位器挂扣配件", "定位器配件", "有防丢需求的宠物主", "专用定位器安装位", "概念"),
        ("刻字定制项圈", "定制服务", "追求个性化的宠物主", "支持宠物名刻字", "概念"),
    ]
    
    spu_ids = []
    for spu_name, category, audience, selling_pts, stage in spu_data:
        c.execute("""INSERT OR IGNORE INTO spus(plan_id, name, category, target_audience, selling_points, stage, owner)
                     VALUES(?,?,?,?,?,?,?)""",
                  (plan_id, spu_name, category, audience, selling_pts, stage, "焦蒙豪"))
        spu_row = c.execute("SELECT id FROM spus WHERE name=? AND plan_id=?", (spu_name, plan_id)).fetchone()
        spu_ids.append(spu_row[0] if spu_row else len(spu_ids) + 1)

    # ===== SKU示例 =====
    if len(spu_ids) >= 1:
        for name, color, size, price in [
            ("基础款-S码", "黑色", "S", 89),
            ("基础款-M码", "黑色", "M", 99),
        ]:
            c.execute("""INSERT OR IGNORE INTO skus(spu_id, name, color, size, status, estimated_price)
                         VALUES(?,?,?,?,?,?)""", (spu_ids[0], name, color, size, "开发中", price))

    if len(spu_ids) >= 2:
        c.execute("""INSERT OR IGNORE INTO skus(spu_id, name, status, estimated_price)
                     VALUES(?,?,?,?)""", (spu_ids[1], "定位器挂扣-通用款", "开发中", 39))

    if len(spu_ids) >= 3:
        for name, price in [
            ("定制项圈-织带款", 49),
            ("定制项圈-真皮款", 79),
        ]:
            c.execute("""INSERT OR IGNORE INTO skus(spu_id, name, has_engraving, status, estimated_price)
                         VALUES(?,?,?,?,?)""", (spu_ids[2], name, 1, "开发中", price))

    # ===== 零部件示例 =====
    sku_row = c.execute("SELECT id FROM skus WHERE spu_id=? LIMIT 1", (spu_ids[0],)).fetchone()
    if sku_row:
        for name, comp_type, unit_price in [
            ("胸背主体", "半成品", 25),
            ("牵引绳", "半成品", 8),
            ("D型扣", "五金件", 2),
            ("织带", "织带", 4),
        ]:
            c.execute("""INSERT OR IGNORE INTO components(sku_id, name, type, unit_price)
                         VALUES(?,?,?,?)""", (sku_row[0], name, comp_type, unit_price))

    # ===== 项目设置 =====
    for k, v in {"project_name": "宠物胸背牵引绳系列开发", "current_phase": "竞品研究", "weekly_goal": "完成竞品调研"}.items():
        c.execute("INSERT OR IGNORE INTO project_settings(key, value) VALUES(?,?)", (k, v))

    # ===== 默认任务 =====
    for i, (no, title, assignee, status, priority, need) in enumerate([
        ("T-001", "收集竞品信息", "焦蒙豪", "进行中", "高", 0),
        ("T-002", "整理竞品差评", "焦蒙豪", "未开始", "高", 0),
        ("T-003", "找胸背工厂", "潘浩博", "进行中", "高", 0),
        ("T-004", "建立成本模板", "潘翔", "未开始", "中", 0),
    ]):
        c.execute("""INSERT INTO tasks(task_no, plan_id, title, assignee, status, priority, need_approval)
                     VALUES(?,?,?,?,?,?,?)""", (no, plan_id, title, assignee, status, priority, need))


# ===================== 用户 =====================
def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_names():
    return ["焦蒙豪", "潘翔", "潘浩博"]

# ===================== 开发计划 =====================
def get_all_plans():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM development_plans ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_plan(plan_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM development_plans WHERE id=?", (plan_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_plan(data):
    conn = get_connection()
    now = datetime.now().isoformat()
    c = conn.execute("""INSERT INTO development_plans(name, description, status, owner, start_date, target_date, created_at, updated_at)
                        VALUES(?,?,?,?,?,?,?,?)""",
                     (data.get("name",""), data.get("description",""), data.get("status","进行中"),
                      data.get("owner","焦蒙豪"), data.get("start_date",""), data.get("target_date",""), now, now))
    conn.commit()
    log_activity("新建开发计划", "plan", c.lastrowid, data.get("owner","焦蒙豪"), data.get("name",""))
    conn.close()
    return c.lastrowid

def update_plan(plan_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [plan_id]
    conn.execute(f"UPDATE development_plans SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def delete_plan(plan_id):
    conn = get_connection()
    p = conn.execute("SELECT name FROM development_plans WHERE id=?", (plan_id,)).fetchone()
    conn.execute("DELETE FROM development_plans WHERE id=?", (plan_id,))
    conn.commit()
    log_activity("删除开发计划", "plan", plan_id, "系统", p["name"] if p else "")
    conn.close()

# ===================== SPU =====================
def get_spus_by_plan(plan_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM spus WHERE plan_id=? ORDER BY id", (plan_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_spus():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM spus ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_spu(spu_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM spus WHERE id=?", (spu_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_spu(data):
    conn = get_connection()
    now = datetime.now().isoformat()
    c = conn.execute("""INSERT INTO spus(plan_id, name, category, positioning, target_audience, selling_points, stage, owner, notes, created_at, updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                     (data.get("plan_id",0), data.get("name",""), data.get("category",""),
                      data.get("positioning",""), data.get("target_audience",""), data.get("selling_points",""),
                      data.get("stage","概念"), data.get("owner","焦蒙豪"), data.get("notes",""), now, now))
    conn.commit()
    log_activity("新建SPU", "spu", c.lastrowid, data.get("owner","焦蒙豪"), data.get("name",""))
    conn.close()
    return c.lastrowid

def update_spu(spu_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [spu_id]
    conn.execute(f"UPDATE spus SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def delete_spu(spu_id):
    conn = get_connection()
    s = conn.execute("SELECT name FROM spus WHERE id=?", (spu_id,)).fetchone()
    conn.execute("DELETE FROM spus WHERE id=?", (spu_id,))
    conn.commit()
    log_activity("删除SPU", "spu", spu_id, "系统", s["name"] if s else "")
    conn.close()

# ===================== SKU =====================
def get_skus_by_spu(spu_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM skus WHERE spu_id=? ORDER BY id", (spu_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_skus():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM skus ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_sku(sku_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM skus WHERE id=?", (sku_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_sku(data):
    conn = get_connection()
    now = datetime.now().isoformat()
    c = conn.execute("""INSERT INTO skus(spu_id, name, color, size, style, specification, has_engraving, has_locator_port, has_locator, estimated_price, status, created_at, updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (data.get("spu_id",0), data.get("name",""), data.get("color",""),
                      data.get("size",""), data.get("style",""), data.get("specification",""),
                      1 if data.get("has_engraving") else 0, 1 if data.get("has_locator_port") else 0,
                      1 if data.get("has_locator") else 0, data.get("estimated_price",0),
                      data.get("status","开发中"), now, now))
    conn.commit()
    conn.close()
    return c.lastrowid

def update_sku(sku_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["has_engraving"] = 1 if data.get("has_engraving") else 0
    data["has_locator_port"] = 1 if data.get("has_locator_port") else 0
    data["has_locator"] = 1 if data.get("has_locator") else 0
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [sku_id]
    conn.execute(f"UPDATE skus SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def delete_sku(sku_id):
    conn = get_connection()
    conn.execute("DELETE FROM skus WHERE id=?", (sku_id,))
    conn.commit()
    conn.close()

# ===================== 零部件 =====================
def get_components_by_sku(sku_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM components WHERE sku_id=? ORDER BY id", (sku_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_components():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM components ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_component(data):
    conn = get_connection()
    now = datetime.now().isoformat()
    c = conn.execute("""INSERT INTO components(sku_id, name, type, quantity, unit, unit_price, supplier, notes, created_at, updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""",
                     (data.get("sku_id",0), data.get("name",""), data.get("type","其他"),
                      data.get("quantity",1), data.get("unit","个"), data.get("unit_price",0),
                      data.get("supplier",""), data.get("notes",""), now, now))
    conn.commit()
    conn.close()
    return c.lastrowid

def update_component(comp_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [comp_id]
    conn.execute(f"UPDATE components SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def delete_component(comp_id):
    conn = get_connection()
    conn.execute("DELETE FROM components WHERE id=?", (comp_id,))
    conn.commit()
    conn.close()

# ===================== 成本明细 =====================
def get_cost_items(plan_id=0, spu_id=0, sku_id=0):
    conn = get_connection()
    query = "SELECT * FROM cost_items_new WHERE 1=1"
    params = []
    if plan_id: query += " AND plan_id=?"; params.append(plan_id)
    if spu_id: query += " AND spu_id=?"; params.append(spu_id)
    if sku_id: query += " AND sku_id=?"; params.append(sku_id)
    query += " ORDER BY sort_order, id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_cost_item(data):
    conn = get_connection()
    now = datetime.now().isoformat()
    data["subtotal"] = data.get("quantity", 1) * data.get("unit_price", 0)
    c = conn.execute("""INSERT INTO cost_items_new(plan_id, spu_id, sku_id, name, category, quantity, unit_price, subtotal, source, sort_order, notes, created_at, updated_at)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (data.get("plan_id",0), data.get("spu_id",0), data.get("sku_id",0),
                      data.get("name",""), data.get("category","物料"), data.get("quantity",1),
                      data.get("unit_price",0), data["subtotal"], data.get("source","手动"),
                      data.get("sort_order",0), data.get("notes",""), now, now))
    conn.commit()
    conn.close()
    return c.lastrowid

def update_cost_item(item_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["subtotal"] = data.get("quantity", 1) * data.get("unit_price", 0)
    sets = ", ".join([f"{k}=?" for k in data.keys()])
    vals = list(data.values()) + [item_id]
    conn.execute(f"UPDATE cost_items_new SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def delete_cost_item(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM cost_items_new WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def reorder_cost_items(item_ids):
    conn = get_connection()
    for idx, item_id in enumerate(item_ids):
        conn.execute("UPDATE cost_items_new SET sort_order=? WHERE id=?", (idx, item_id))
    conn.commit()
    conn.close()

# ===================== 任务 =====================
def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tasks_by_plan(plan_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks WHERE plan_id=? ORDER BY id DESC", (plan_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_task(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_task(data):
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
    task_no = f"T-{row[0]+1:03d}"
    now = datetime.now().isoformat()
    c = conn.execute("""INSERT INTO tasks(task_no, plan_id, spu_id, task_type, module, title, description, assignee, helper, deadline,
                 status, priority, progress, blocker, next_action, need_approval, created_at, updated_at)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (task_no, data.get("plan_id",0), data.get("spu_id",0), data.get("task_type",""),
                  data.get("module",""), data.get("title",""), data.get("description",""),
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

# ===================== 竞品 =====================
def get_all_competitors():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM competitors ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_competitors_by_plan_spu(plan_id=0, spu_id=0):
    conn = get_connection()
    query = "SELECT * FROM competitors WHERE 1=1"
    params = []
    if plan_id: query += " AND plan_id=?"; params.append(plan_id)
    if spu_id: query += " AND spu_id=?"; params.append(spu_id)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_competitor(data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["is_key"] = 1 if data.get("is_key") else 0
    data["has_engraving"] = 1 if data.get("has_engraving") else 0
    data["has_locator"] = 1 if data.get("has_locator") else 0
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO competitors({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    log_activity("新增竞品", "competitor", c.lastrowid, "焦蒙豪", data.get("name",""))
    conn.close()
    return c.lastrowid

def update_competitor(comp_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["is_key"] = 1 if data.get("is_key") else 0
    data["has_engraving"] = 1 if data.get("has_engraving") else 0
    data["has_locator"] = 1 if data.get("has_locator") else 0
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

# ===================== 产品需求 =====================
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

# ===================== 样品 =====================
def get_all_samples():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM samples ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_samples_by_plan_spu(plan_id=0, spu_id=0):
    conn = get_connection()
    query = "SELECT * FROM samples WHERE 1=1"
    params = []
    if plan_id: query += " AND plan_id=?"; params.append(plan_id)
    if spu_id: query += " AND spu_id=?"; params.append(spu_id)
    query += " ORDER BY updated_at DESC"
    rows = conn.execute(query, params).fetchall()
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
    log_activity("新增样品", "sample", c.lastrowid, data.get("owner","潘浩博"), data.get("sample_content",""))
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

# ===================== 供应商 =====================
def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM suppliers ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_supplier_names():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT name FROM suppliers ORDER BY name").fetchall()
    conn.close()
    return [r["name"] for r in rows]

def create_supplier(data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["supports_engraving"] = 1 if data.get("supports_engraving") else 0
    data["supports_logo"] = 1 if data.get("supports_logo") else 0
    data["supports_locator_parts"] = 1 if data.get("supports_locator_parts") else 0
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c = conn.execute(f"INSERT INTO suppliers({cols}) VALUES({placeholders})", list(data.values()))
    conn.commit()
    log_activity("新增供应商", "supplier", c.lastrowid, "潘浩博", data.get("name",""))
    conn.close()
    return c.lastrowid

def update_supplier(sup_id, data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["supports_engraving"] = 1 if data.get("supports_engraving") else 0
    data["supports_logo"] = 1 if data.get("supports_logo") else 0
    data["supports_locator_parts"] = 1 if data.get("supports_locator_parts") else 0
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

# ===================== 成本利润 =====================
def get_all_costs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cost_profit ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_costs_by_sku(sku_id=0):
    conn = get_connection()
    if sku_id:
        rows = conn.execute("SELECT * FROM cost_profit WHERE sku_id=? ORDER BY id", (sku_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM cost_profit ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_cost(data):
    conn = get_connection()
    data["updated_at"] = datetime.now().isoformat()
    data["total_cost"] = sum([
        data.get("chest_harness_cost", 0) or 0, data.get("leash_cost", 0) or 0,
        data.get("hardware_cost", 0) or 0, data.get("airtag_structure_cost", 0) or 0,
        data.get("customization_cost", 0) or 0, data.get("packaging_cost", 0) or 0,
        data.get("labor_cost", 0) or 0, data.get("shipping_cost", 0) or 0,
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
        data.get("chest_harness_cost", 0) or 0, data.get("leash_cost", 0) or 0,
        data.get("hardware_cost", 0) or 0, data.get("airtag_structure_cost", 0) or 0,
        data.get("customization_cost", 0) or 0, data.get("packaging_cost", 0) or 0,
        data.get("labor_cost", 0) or 0, data.get("shipping_cost", 0) or 0,
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
def get_task_stats(plan_id=0):
    conn = get_connection()
    stats = {}
    base = f"SELECT COUNT(*) FROM tasks{' WHERE plan_id=' + str(plan_id) if plan_id else ''}"
    stats["total"] = conn.execute(base).fetchone()[0]
    stats["in_progress"] = conn.execute(f"{base} AND status='进行中'").fetchone()[0]
    stats["completed"] = conn.execute(f"{base} AND status='已完成'").fetchone()[0]
    stats["at_risk"] = conn.execute(f"{base} AND status='有风险'").fetchone()[0]
    stats["not_started"] = conn.execute(f"{base} AND status='未开始'").fetchone()[0]
    stats["waiting"] = conn.execute(f"{base} AND status='等待中'").fetchone()[0]
    today = datetime.now().strftime("%Y-%m-%d")
    stats["overdue"] = conn.execute(f"{base} AND deadline != '' AND deadline < '{today}' AND status NOT IN ('已完成','已取消')").fetchone()[0]
    conn.close()
    return stats

def get_overdue_tasks(plan_id=0):
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    query = "SELECT * FROM tasks WHERE deadline != '' AND deadline < ? AND status NOT IN ('已完成','已取消')"
    params = [today]
    if plan_id: query += " AND plan_id=?"; params.append(plan_id)
    query += " ORDER BY deadline"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_risk_tasks(plan_id=0):
    conn = get_connection()
    query = "SELECT * FROM tasks WHERE status='有风险'"
    if plan_id: query += f" AND plan_id={plan_id}"
    query += " ORDER BY deadline"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_approval_tasks(plan_id=0):
    conn = get_connection()
    query = "SELECT * FROM tasks WHERE need_approval=1 AND status NOT IN ('已完成','已取消')"
    if plan_id: query += f" AND plan_id={plan_id}"
    query += " ORDER BY created_at"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_logs(limit=10):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_plan_stats(plan_id):
    conn = get_connection()
    stats = {}
    stats["spu_count"] = conn.execute("SELECT COUNT(*) FROM spus WHERE plan_id=?", (plan_id,)).fetchone()[0]
    stats["sku_count"] = conn.execute("""SELECT COUNT(*) FROM skus s JOIN spus ON s.spu_id=spus.id WHERE spus.plan_id=?""", (plan_id,)).fetchone()[0]
    stats["sample_in_progress"] = conn.execute("""SELECT COUNT(*) FROM samples s JOIN spus ON s.spu_id=spus.id WHERE spus.plan_id=? AND s.status IN ('打样中','已寄出','测试中')""", (plan_id,)).fetchone()[0]
    stats["total_cost"] = conn.execute("SELECT COALESCE(SUM(total_cost), 0) FROM cost_profit WHERE plan_id=?", (plan_id,)).fetchone()[0]
    conn.close()
    return stats
