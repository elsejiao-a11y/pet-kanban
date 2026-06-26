import streamlit as st
import db

# ===== 页面配置 =====
st.set_page_config(
    page_title="宠物用品项目看板",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== 初始化数据库 =====
db.init_db()

# ===== 自定义样式 =====
st.markdown("""
<style>
    .stApp {{ max-width: 1200px; margin: 0 auto; }}
    .stat-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }}
    .stat-card h2 {{ color: white; margin: 0; font-size: 2em; }}
    .stat-card p {{ margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.9; }}
    .stat-card.blue {{ background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%); }}
    .stat-card.green {{ background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); }}
    .stat-card.red {{ background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); }}
    .stat-card.orange {{ background: linear-gradient(135deg, #F39C12 0%, #E67E22 100%); }}
    .stat-card.gray {{ background: linear-gradient(135deg, #95A5A6 0%, #7F8C8D 100%); }}
    .stat-card.purple {{ background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%); }}
    .status-badge {{
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        display: inline-block;
        color: white;
    }}
    .status-未开始 {{ background-color: #95A5A6; }}
    .status-进行中 {{ background-color: #3498DB; }}
    .status-等待中 {{ background-color: #F39C12; }}
    .status-有风险 {{ background-color: #E74C3C; }}
    .status-已完成 {{ background-color: #2ECC71; }}
    .status-已取消 {{ background-color: #BDC3C7; color: #666; }}
    .priority-高 {{ color: #E74C3C; font-weight: bold; }}
    .priority-中 {{ color: #F39C12; font-weight: bold; }}
    .priority-低 {{ color: #95A5A6; }}
    .task-card {{
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .task-card h4 {{ margin: 0 0 8px 0; }}
    .task-card .meta {{ color: #888; font-size: 0.85em; }}
    .alert-card {{
        background: #FFF3CD;
        border: 1px solid #FFEEBA;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }}
    .alert-card.danger {{
        background: #F8D7DA;
        border: 1px solid #F5C6CB;
    }}
    .alert-card.info {{
        background: #D1ECF1;
        border: 1px solid #BEE5EB;
    }}
    footer {{ visibility: hidden; }}
    @media (max-width: 768px) {{
        .stat-card h2 {{ font-size: 1.5em; }}
        .stat-card {{ padding: 12px; }}
    }}
</style>
""", unsafe_allow_html=True)

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("## 🐾 宠物用品项目看板")
    st.markdown("---")
    current_user = st.selectbox(
        "当前用户",
        ["阿豪", "潘翔", "浩博"],
        index=0,
        key="current_user",
    )
    st.session_state["current_user"] = current_user
    roles = {{
        "阿豪": "📋 项目负责人 / 产品负责人",
        "潘翔": "💰 财务负责人 / 执行跟进",
        "浩博": "🏭 生产负责人 / 供应链负责人",
    }}
    st.markdown(f"**{current_user}**\n\n{roles.get(current_user, '')}")
    st.markdown("---")
    st.markdown("### 项目阶段")
    phase = db.get_setting("current_phase", "竞品研究")
    phases = ["竞品研究", "打样准备", "打样中", "测试中", "小批量准备"]
    phase_idx = phases.index(phase) if phase in phases else 0
    for i, p in enumerate(phases):
        icon = "🟢" if i < phase_idx else ("🔵" if i == phase_idx else "⚪")
        st.markdown(f"{icon} {p}")
    st.markdown("---")
    st.caption("v1.0 · 内部协作看板")
