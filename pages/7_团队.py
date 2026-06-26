import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 👥 团队成员")

current_user = st.session_state.get("current_user", "阿豪")

# ===== 成员信息 =====
members = [
    {
        "name": "阿豪",
        "role": "项目负责人 / 产品负责人",
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
        "role": "财务负责人 / 执行跟进",
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
            "✅ 可以编辑任务",
            "✅ 可以编辑财务成本",
            "✅ 可以编辑供应商资料",
            "✅ 可以查看产品和打样信息",
            "⚠️ 不建议删除核心数据",
        ],
    },
    {
        "name": "浩博",
        "role": "生产负责人 / 供应链负责人",
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
            "✅ 可以编辑任务",
            "✅ 可以编辑打样生产",
            "✅ 可以编辑供应商资料",
            "✅ 可以查看产品和财务信息",
            "⚠️ 不建议删除核心数据",
        ],
    },
]

# 显示当前用户
st.markdown(f"### 当前身份：{[m for m in members if m['name'] == current_user][0]['emoji']} {current_user}")
st.caption(f"角色：{[m for m in members if m['name'] == current_user][0]['role']}")

st.markdown("---")

# ===== 成员卡片 =====
for member in members:
    with st.container():
        st.markdown(f"### {member['emoji']} {member['name']}")
        st.markdown(f"**{member['role']}**")
        
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
        st.divider()

# ===== 项目设置（仅管理员可见） =====
if current_user == "阿豪":
    st.markdown("---")
    st.markdown("### ⚙️ 项目设置")
    
    with st.form("settings_form"):
        project_name = st.text_input("项目名称", value=db.get_setting("project_name", "宠物胸背牵引绳项目"))
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
