import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 👥 团队成员")

current_user = st.session_state.get("current_user", "焦蒙豪")

# ===== 成员信息 =====
members = [
    {
        "name": "焦蒙豪",
        "role": "管理员",
        "emoji": "📋",
        "color": "#E74C3C",
        "responsibilities": [
            "找产品、研究产品",
            "竞品分析",
            "产品优化",
            "卖点设计",
            "最终拍板决策",
        ],
        "permissions": [
            "✅ 可以新增、编辑、删除所有内容",
            "✅ 可以查看所有数据",
            "✅ 可以修改项目阶段",
            "✅ 可以标记是否通过",
            "✅ 可以最终拍板",
        ],
    },
    {
        "name": "潘翔",
        "role": "管理员",
        "emoji": "💰",
        "color": "#3498DB",
        "responsibilities": [
            "成本表维护",
            "报价记录",
            "打样费用管理",
            "现金流管理",
            "供应商资料整理",
            "任务跟进",
            "会议记录",
        ],
        "permissions": [
            "✅ 可以新增、编辑、删除所有内容",
            "✅ 可以查看所有数据",
            "✅ 可以管理财务成本",
            "✅ 可以记录供应商报价",
            "✅ 可以修改项目设置",
        ],
    },
    {
        "name": "潘浩博",
        "role": "管理员",
        "emoji": "🏭",
        "color": "#2ECC71",
        "responsibilities": [
            "找工厂",
            "打样管理",
            "工艺评估",
            "结构方案设计",
            "质检",
            "量产可行性评估",
            "交期控制",
        ],
        "permissions": [
            "✅ 可以新增、编辑、删除所有内容",
            "✅ 可以查看所有数据",
            "✅ 可以管理打样生产",
            "✅ 可以管理供应商资料",
            "✅ 可以修改项目设置",
        ],
    },
]

# 显示当前用户
st.markdown(f"### 当前身份：{[m for m in members if m['name'] == current_user][0]['emoji']} {current_user}")
st.markdown(f"**角色：** {[m for m in members if m['name'] == current_user][0]['role']}")

st.markdown("---")

# ===== 成员卡片 =====
for member in members:
    with st.container():
        st.markdown(f"### {member['emoji']} {member['name']}")
        st.markdown(f"**角色：** {member['role']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📌 职责范围：**")
            for resp in member["responsibilities"]:
                st.markdown(f"- {resp}")
        with c2:
            st.markdown("**🔐 权限：**")
            for perm in member["permissions"]:
                st.markdown(f"- {perm}")
        
        # 显示该成员的任务统计
        all_tasks = db.get_all_tasks()
        my_tasks = [t for t in all_tasks if t["assignee"] == member["name"] or t["helper"] == member["name"]]
        in_progress = len([t for t in my_tasks if t["status"] == "进行中"])
        completed = len([t for t in my_tasks if t["status"] == "已完成"])
        pending = len([t for t in my_tasks if t["status"] in ("未开始", "等待中")])
        
        st.markdown(f"**📊 任务统计：** 进行中 {in_progress} | 待处理 {pending} | 已完成 {completed} | 总计 {len(my_tasks)}")
        
        # 快速查看该成员的任务
        with st.expander(f"查看 {member['name']} 的任务"):
            if my_tasks:
                for t in my_tasks[:10]:
                    status_class = f"status-{t['status']}"
                    st.markdown(f"- **{t['task_no']}** {t['title']} - <span class='{status_class}'>{t['status']}</span>", unsafe_allow_html=True)
            else:
                st.info("暂无任务")
        
        st.divider()

# ===== 项目设置（所有管理员都可以修改） =====
st.markdown("---")
st.markdown("### ⚙️ 项目设置")

with st.form("settings_form"):
    project_name = st.text_input("项目名称", value=db.get_setting("project_name", "宠物胸背牵引绳系列开发"))
    current_phase = st.selectbox("当前阶段", 
                                 ["竞品研究", "打样准备", "打样中", "测试中", "小批量准备"],
                                 index=["竞品研究", "打样准备", "打样中", "测试中", "小批量准备"].index(
                                     db.get_setting("current_phase", "竞品研究")))
    weekly_goal = st.text_area("本周目标", value=db.get_setting("weekly_goal", ""), height=80)
    
    if st.form_submit_button("💾 保存设置", type="primary"):
        db.set_setting("project_name", project_name)
        db.set_setting("current_phase", current_phase)
        db.set_setting("weekly_goal", weekly_goal)
        st.success("设置已保存！")
        st.rerun()
