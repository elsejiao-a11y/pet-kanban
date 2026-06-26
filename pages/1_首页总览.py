import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🏠 首页总览")

# 项目基本信息
project_name = db.get_setting("project_name", "宠物胸背牵引绳项目")
current_phase = db.get_setting("current_phase", "竞品研究")
weekly_goal = db.get_setting("weekly_goal", "")

st.markdown(f"### 📌 {project_name}")
st.markdown(f"**当前阶段：** {current_phase}")

# 阶段进度条
phases = ["竞品研究", "打样准备", "打样中", "测试中", "小批量准备"]
phase_idx = phases.index(current_phase) if current_phase in phases else 0

cols = st.columns(len(phases))
for i, (col, p) in enumerate(zip(cols, phases)):
    with col:
        if i < phase_idx:
            st.markdown(f'<div style="text-align:center;padding:8px;background:#2ECC71;color:white;border-radius:8px;font-size:0.85em">✅ {p}</div>', unsafe_allow_html=True)
        elif i == phase_idx:
            st.markdown(f'<div style="text-align:center;padding:8px;background:#4A90D9;color:white;border-radius:8px;font-size:0.85em;font-weight:bold">🔵 {p}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align:center;padding:8px;background:#ECF0F1;color:#999;border-radius:8px;font-size:0.85em">⚪ {p}</div>', unsafe_allow_html=True)

st.markdown("---")

# ===== 统计卡片 =====
stats = db.get_task_stats()

cols = st.columns(6)
card_configs = [
    (stats["total"], "总任务", "purple"),
    (stats["in_progress"], "进行中", "blue"),
    (stats["completed"], "已完成", "green"),
    (stats["at_risk"], "有风险", "red"),
    (stats["overdue"], "已延期", "orange"),
    (stats["waiting"], "等待中", "gray"),
]
for col, (num, label, color) in zip(cols, card_configs):
    with col:
        st.markdown(f"""
        <div class="stat-card {color}">
            <h2>{num}</h2>
            <p>{label}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ===== 本周目标 =====
if weekly_goal:
    st.markdown("### 🎯 本周目标")
    st.info(weekly_goal)

# ===== 两列布局 =====
left, right = st.columns(2)

# ===== 左侧：今日重点任务 + 需要拍板 =====
with left:
    st.markdown("### 📋 今日重点任务")
    all_tasks = db.get_all_tasks()
    today_tasks = [t for t in all_tasks if t["priority"] == "高" and t["status"] not in ("已完成", "已取消")]
    if today_tasks:
        for t in today_tasks[:5]:
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

    st.markdown("### ⚠️ 需要阿豪拍板")
    approval_tasks = db.get_approval_tasks()
    if approval_tasks:
        for t in approval_tasks:
            st.markdown(f"""
            <div class="alert-card">
                <strong>{t['task_no']} {t['title']}</strong><br>
                <span style="color:#888;font-size:0.85em">负责人：{t['assignee']} | 状态：{t['status']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("暂无待拍板事项 ✅")

# ===== 右侧：延期任务 + 有风险任务 + 最近更新 =====
with right:
    st.markdown("### 🔴 延期任务")
    overdue_tasks = db.get_overdue_tasks()
    if overdue_tasks:
        for t in overdue_tasks:
            st.markdown(f"""
            <div class="alert-card danger">
                <strong>{t['task_no']} {t['title']}</strong><br>
                <span style="color:#888;font-size:0.85em">
                    负责人：{t['assignee']} | 截止：{t['deadline']} | 状态：{t['status']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("暂无延期任务 ✅")

    st.markdown("### 🟡 有风险任务")
    risk_tasks = db.get_risk_tasks()
    if risk_tasks:
        for t in risk_tasks:
            st.markdown(f"""
            <div class="alert-card">
                <strong>{t['task_no']} {t['title']}</strong><br>
                <span style="color:#888;font-size:0.85em">
                    负责人：{t['assignee']} | 卡点：{t.get('blocker','无')}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("暂无风险任务 ✅")

    st.markdown("### 📝 最近更新")
    logs = db.get_recent_logs(5)
    if logs:
        for log in logs:
            st.markdown(f"- {log['detail']}（{log['action']} · {log['user']}）")
    else:
        st.caption("暂无更新记录")
