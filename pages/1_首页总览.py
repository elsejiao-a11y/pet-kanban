import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🏠 首页总览")

# 获取当前计划和统计
plan_id = st.session_state.get("current_plan_id", 0)
current_plan = db.get_plan(plan_id) if plan_id else None
stats = db.get_plan_stats(plan_id) if plan_id else {}

# ===== 计划概览 =====
if current_plan:
    st.markdown(f"### 📌 {current_plan['name']}")
    st.markdown(f"**状态：** {current_plan['status']} | **负责人：** {current_plan['owner']}")
    if current_plan.get("description"):
        st.caption(current_plan["description"])
else:
    st.info("请先在侧边栏选择或创建开发计划")

# ===== 统计卡片 =====
cols = st.columns(4)
card_data = [
    (stats.get("spu_count", 0), "SPU数量", "purple"),
    (stats.get("sku_count", 0), "SKU数量", "blue"),
    (stats.get("sample_in_progress", 0), "进行中样品", "orange"),
    (stats.get("total_cost", 0), "总成本(元)", "green"),
]
for col, (num, label, color) in zip(cols, card_data):
    with col:
        st.markdown(f"""
        <div class="stat-card {color}">
            <h2>{num}</h2>
            <p>{label}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ===== 阶段进度条 =====
st.markdown("### 📊 产品阶段进度")
spus = db.get_spus_by_plan(plan_id) if plan_id else []
if spus:
    stages = ["概念", "规划", "设计", "打样", "测试", "上市"]
    stage_counts = {s: 0 for s in stages}
    for spu in spus:
        if spu["stage"] in stage_counts:
            stage_counts[spu["stage"]] += 1
    
    cols = st.columns(len(stages))
    for i, (col, stage) in enumerate(zip(cols, stages)):
        with col:
            count = stage_counts[stage]
            if count > 0:
                st.markdown(f'<div style="text-align:center;padding:8px;background:#2ECC71;color:white;border-radius:8px;font-size:0.85em">✅ {stage}<br>{count}个</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align:center;padding:8px;background:#ECF0F1;color:#999;border-radius:8px;font-size:0.85em">⚪ {stage}</div>', unsafe_allow_html=True)
else:
    st.info("暂无产品数据")

st.markdown("---")

# ===== 本周目标 =====
weekly_goal = db.get_setting("weekly_goal", "")
if weekly_goal:
    st.markdown("### 🎯 本周目标")
    st.info(weekly_goal)

# ===== 快捷入口 =====
st.markdown("### 🚀 快捷入口")
quick_links = [
    ("📋 任务看板", "2_任务看板", "查看和管理任务"),
    ("📦 产品开发", "3_产品开发", "管理SPU/SKU和零部件"),
    ("🔬 竞品分析", "4_竞品分析", "分析竞争对手"),
    ("🏭 打样生产", "5_打样生产", "管理样品进度"),
    ("🏢 供应商", "6_供应商管理", "管理供应商资料"),
    ("💰 财务成本", "7_财务成本", "成本和利润分析"),
]
cols = st.columns(3)
for i, (name, page, desc) in enumerate(quick_links):
    with cols[i % 3]:
        st.page_link(f"pages/{page}.py", label=f"{name}\n{desc}", use_container_width=True)

st.markdown("---")

# ===== 两列布局 =====
left, right = st.columns(2)

with left:
    st.markdown("### 📋 今日重点任务")
    tasks = db.get_tasks_by_plan(plan_id) if plan_id else db.get_all_tasks()
    high_priority = [t for t in tasks if t["priority"] == "高" and t["status"] not in ("已完成", "已取消")]
    if high_priority:
        for t in high_priority[:5]:
            status_class = f"status-{t['status']}"
            st.markdown(f"""
            <div class="task-card">
                <h4>{t['task_no']} {t['title']}</h4>
                <div class="meta">
                    <span class="status-badge {status_class}">{t['status']}</span>
                    &nbsp; 👤 {t['assignee']}
                    &nbsp; 📅 {t['deadline'] or '未设定'}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("暂无高优先级任务 ✨")

with right:
    st.markdown("### ⚠️ 需要关注的任务")
    overdue = db.get_overdue_tasks(plan_id) if plan_id else []
    risk = db.get_risk_tasks(plan_id) if plan_id else []
    
    if overdue:
        st.markdown("#### 🔴 延期任务")
        for t in overdue[:3]:
            st.markdown(f"""
            <div class="alert-card danger">
                <strong>{t['task_no']} {t['title']}</strong><br>
                <span style="color:#888;font-size:0.85em">
                    负责人：{t['assignee']} | 截止：{t['deadline']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    if risk:
        st.markdown("#### 🟡 有风险任务")
        for t in risk[:3]:
            st.markdown(f"""
            <div class="alert-card">
                <strong>{t['task_no']} {t['title']}</strong><br>
                <span style="color:#888;font-size:0.85em">
                    负责人：{t['assignee']} | 卡点：{t.get('blocker','无')}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    if not overdue and not risk:
        st.success("暂无风险或延期任务 ✅")

st.markdown("---")

# ===== 最近更新 =====
st.markdown("### 📝 最近更新")
logs = db.get_recent_logs(5)
if logs:
    for log in logs:
        st.markdown(f"- {log['detail']}（{log['action']} · {log['user']}）")
else:
    st.caption("暂无更新记录")
