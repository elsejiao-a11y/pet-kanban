import streamlit as st
import db

# ===== 页面配置 =====
st.set_page_config(
    page_title="宠物用品新品开发系统",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== 初始化数据库 =====
db.init_db()

# ===== 自定义样式 =====
st.markdown("""
<style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-card h2 { color: white; margin: 0; font-size: 2em; }
    .stat-card p { margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.9; }
    .stat-card.blue { background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%); }
    .stat-card.green { background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); }
    .stat-card.red { background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); }
    .stat-card.orange { background: linear-gradient(135deg, #F39C12 0%, #E67E22 100%); }
    .stat-card.gray { background: linear-gradient(135deg, #95A5A6 0%, #7F8C8D 100%); }
    .stat-card.purple { background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%); }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        display: inline-block;
        color: white;
    }
    .status-未开始 { background-color: #95A5A6; }
    .status-进行中 { background-color: #3498DB; }
    .status-等待中 { background-color: #F39C12; }
    .status-有风险 { background-color: #E74C3C; }
    .status-已完成 { background-color: #2ECC71; }
    .status-已取消 { background-color: #BDC3C7; color: #666; }
    .priority-高 { color: #E74C3C; font-weight: bold; }
    .priority-中 { color: #F39C12; font-weight: bold; }
    .priority-低 { color: #95A5A6; }
    .task-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .task-card h4 { margin: 0 0 8px 0; }
    .task-card .meta { color: #888; font-size: 0.85em; }
    .alert-card {
        background: #FFF3CD;
        border: 1px solid #FFEEBA;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .alert-card.danger { background: #F8D7DA; border: 1px solid #F5C6CB; }
    footer { visibility: hidden; }
    @media (max-width: 768px) {
        .stat-card h2 { font-size: 1.5em; }
        .stat-card { padding: 12px; }
    }
</style>
""", unsafe_allow_html=True)

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## 🐾 宠物用品新品开发系统")
    st.markdown("---")
    
    # 初始化session_state
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = "焦蒙豪"
    if "current_plan_id" not in st.session_state:
        plans = db.get_all_plans()
        st.session_state["current_plan_id"] = plans[0]["id"] if plans else 0
    
    # 当前用户选择
    user_names = db.get_user_names()
    current_user = st.selectbox(
        "当前用户",
        user_names,
        index=user_names.index(st.session_state["current_user"]) if st.session_state["current_user"] in user_names else 0,
        key="sel_current_user",
    )
    st.session_state["current_user"] = current_user
    
    # 角色显示（三人都是管理员）
    st.markdown(f"**{current_user}**  |  管理员")
    
    st.markdown("---")
    
    # 当前开发计划选择
    plans = db.get_all_plans()
    if plans:
        plan_options = {p["id"]: p["name"] for p in plans}
        selected_plan_id = st.selectbox(
            "📋 当前开发计划",
            options=list(plan_options.keys()),
            format_func=lambda x: plan_options[x],
            index=list(plan_options.keys()).index(st.session_state["current_plan_id"]) if st.session_state["current_plan_id"] in plan_options else 0,
            key="sel_plan"
        )
        st.session_state["current_plan_id"] = selected_plan_id
        
        # 显示计划状态
        current_plan = db.get_plan(selected_plan_id)
        if current_plan:
            st.caption(f"状态: {current_plan['status']} | 负责人: {current_plan['owner']}")
    else:
        st.info("暂无开发计划")
    
    st.markdown("---")
    st.markdown("### 快捷导航")
    
    # 导航顺序
    nav_items = [
        ("首页总览", "1_首页总览"),
        ("任务看板", "2_任务看板"),
        ("产品开发", "3_产品开发"),
        ("竞品分析", "4_竞品分析"),
        ("打样生产", "5_打样生产"),
        ("供应商管理", "6_供应商管理"),
        ("财务成本", "7_财务成本"),
        ("团队成员", "8_团队"),
    ]
    
    for name, page in nav_items:
        st.page_link(f"pages/{page}.py", label=name)
    
    st.markdown("---")
    st.caption("v2.0 · 新品开发系统")
