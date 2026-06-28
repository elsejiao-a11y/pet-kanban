import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 📋 任务看板")

current_user = st.session_state.get("current_user", "焦蒙豪")
plan_id = st.session_state.get("current_plan_id", 0)

# ===== 获取数据 =====
all_tasks = db.get_all_tasks()
plans = db.get_all_plans()
spus = db.get_spus_by_plan(plan_id) if plan_id else []

# ===== 筛选栏 =====
task_types = ["全部", "竞品分析", "需求整理", "打样跟进", "供应商沟通", "成本测算", "页面资料", "上架准备", "测试反馈", "其他"]
statuses = ["全部", "未开始", "进行中", "等待中", "有风险", "已完成", "已取消"]
assignees = ["全部"] + db.get_user_names()
priorities = ["全部", "高", "中", "低"]

# 第一行筛选
fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    filter_type = st.selectbox("任务类型", task_types, key="filter_type")
with fc2:
    filter_status = st.selectbox("状态", statuses, key="filter_status")
with fc3:
    filter_assignee = st.selectbox("负责人", assignees, key="filter_assign")
with fc4:
    filter_priority = st.selectbox("优先级", priorities, key="filter_priority")

# 第二行快捷筛选
qc1, qc2, qc3, qc4 = st.columns(4)
with qc1:
    show_mine = st.checkbox("👤 我的任务", key="show_mine")
with qc2:
    show_overdue = st.checkbox("🔴 延期任务", key="show_overdue")
with qc3:
    show_risk = st.checkbox("🟡 有风险", key="show_risk")
with qc4:
    show_approval = st.checkbox("⚡ 需拍板", key="show_approval")

# 应用筛选
filtered = all_tasks
if filter_type != "全部":
    filtered = [t for t in filtered if t["task_type"] == filter_type]
if filter_status != "全部":
    filtered = [t for t in filtered if t["status"] == filter_status]
if filter_assignee != "全部":
    filtered = [t for t in filtered if t["assignee"] == filter_assignee]
if filter_priority != "全部":
    filtered = [t for t in filtered if t["priority"] == filter_priority]
if show_mine:
    filtered = [t for t in filtered if t["assignee"] == current_user or t["helper"] == current_user]
if show_overdue:
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    filtered = [t for t in filtered if t["deadline"] and t["deadline"] < today and t["status"] not in ("已完成", "已取消")]
if show_risk:
    filtered = [t for t in filtered if t["status"] == "有风险"]
if show_approval:
    filtered = [t for t in filtered if t["need_approval"] == 1 and t["status"] not in ("已完成", "已取消")]

st.markdown(f"**共 {len(filtered)} 个任务**")

# ===== 新增任务按钮 =====
if st.button("➕ 新增任务", type="primary", use_container_width=True):
    st.session_state["show_new_task"] = True

# ===== 新增/编辑任务表单 =====
if st.session_state.get("show_new_task") or st.session_state.get("editing_task"):
    is_edit = st.session_state.get("editing_task") is not None
    edit_data = st.session_state.get("editing_task")
    
    st.markdown("---")
    st.markdown(f"### {'✏️ 编辑任务' if is_edit else '➕ 新增任务'}")
    
    with st.form("task_form", clear_on_submit=True):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            title = st.text_input("任务名称 *", value=edit_data["title"] if is_edit else "")
            # 所属开发计划
            plan_options = {p["id"]: p["name"] for p in plans}
            selected_plan = st.selectbox(
                "所属开发计划",
                options=list(plan_options.keys()),
                format_func=lambda x: plan_options.get(x, "未选择"),
                index=list(plan_options.keys()).index(edit_data["plan_id"]) if is_edit and edit_data["plan_id"] in plan_options else 0
            )
            # SPU（可选）
            plan_spus = db.get_spus_by_plan(selected_plan) if selected_plan else []
            spu_options = {0: "无关联SPU"} | {s["id"]: s["name"] for s in plan_spus}
            selected_spu = st.selectbox(
                "关联SPU（可选）",
                options=list(spu_options.keys()),
                format_func=lambda x: spu_options.get(x, "无"),
                index=list(spu_options.keys()).index(edit_data["spu_id"]) if is_edit and edit_data["spu_id"] in spu_options else 0
            )
            task_type = st.selectbox("任务类型", task_types[1:],
                index=task_types[1:].index(edit_data["task_type"]) if is_edit and edit_data["task_type"] in task_types[1:] else 0)
        with r1c2:
            assignee = st.selectbox("负责人", db.get_user_names(),
                index=db.get_user_names().index(edit_data["assignee"]) if is_edit and edit_data["assignee"] in db.get_user_names() else 0)
            priority = st.selectbox("优先级", priorities[1:],
                index=priorities[1:].index(edit_data["priority"]) if is_edit and edit_data["priority"] in priorities[1:] else 1)
            status = st.selectbox("状态", statuses[1:],
                index=statuses[1:].index(edit_data["status"]) if is_edit and edit_data["status"] in statuses[1:] else 0)
            deadline = st.date_input("截止时间", value=None)
        
        helper = st.text_input("协助人", value=edit_data["helper"] if is_edit else "")
        need_approval = st.checkbox("需要确认/拍板", value=bool(edit_data["need_approval"]) if is_edit else False)
        description = st.text_area("任务说明", value=edit_data["description"] if is_edit else "", height=80)
        
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            progress = st.text_input("当前进展", value=edit_data["progress"] if is_edit else "")
        with r2c2:
            blocker = st.text_input("卡点", value=edit_data["blocker"] if is_edit else "")
        with r2c3:
            next_action = st.text_input("下步动作", value=edit_data["next_action"] if is_edit else "")
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("取消", use_container_width=True)
        
        if submitted:
            data = {
                "title": title, "plan_id": selected_plan, "spu_id": selected_spu,
                "task_type": task_type, "assignee": assignee, "status": status,
                "priority": priority, "deadline": deadline.strftime("%Y-%m-%d") if deadline else "",
                "helper": helper, "need_approval": need_approval, "description": description,
                "progress": progress, "blocker": blocker, "next_action": next_action,
            }
            if is_edit:
                db.update_task(edit_data["id"], data)
                st.success(f"任务 {edit_data['task_no']} 已更新！")
                st.session_state.pop("editing_task", None)
            else:
                db.create_task(data)
                st.success("任务创建成功！")
                st.session_state.pop("show_new_task", None)
            st.rerun()
        
        if cancelled:
            st.session_state.pop("show_new_task", None)
            st.session_state.pop("editing_task", None)
            st.rerun()

# ===== 任务列表 =====
st.markdown("---")

if not filtered:
    st.info("暂无符合条件的任务")
else:
    status_order = ["有风险", "进行中", "等待中", "未开始", "已完成", "已取消"]
    for status_name in status_order:
        status_tasks = [t for t in filtered if t["status"] == status_name]
        if not status_tasks:
            continue
        
        status_colors = {"未开始": "#95A5A6", "进行中": "#3498DB", "等待中": "#F39C12",
                        "有风险": "#E74C3C", "已完成": "#2ECC71", "已取消": "#BDC3C7"}
        color = status_colors.get(status_name, "#999")
        st.markdown(f"#### <span style='color:{color}'>● {status_name}</span>（{len(status_tasks)}）", unsafe_allow_html=True)
        
        for t in status_tasks:
            with st.container():
                tc1, tc2, tc3, tc4, tc5 = st.columns([0.5, 2.5, 1, 1, 1])
                with tc1:
                    st.markdown(f"**{t['task_no']}**")
                with tc2:
                    title_text = t["title"]
                    if t["need_approval"]:
                        title_text = f"⚡ {title_text}"
                    st.markdown(f"**{title_text}**")
                    meta_parts = []
                    if t["task_type"]:
                        meta_parts.append(f"📁 {t['task_type']}")
                    if t["blocker"]:
                        meta_parts.append(f"🚧 {t['blocker']}")
                    if meta_parts:
                        st.caption(" | ".join(meta_parts))
                with tc3:
                    st.markdown(f"👤 {t['assignee']}")
                    if t["helper"]:
                        st.caption(f"协助: {t['helper']}")
                with tc4:
                    priority_colors = {"高": "🔴", "中": "🟡", "低": "⚪"}
                    st.markdown(f"{priority_colors.get(t['priority'],'')} {t['priority']}")
                    if t["deadline"]:
                        from datetime import datetime
                        try:
                            dl = datetime.strptime(t["deadline"], "%Y-%m-%d")
                            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                            if dl < today and t["status"] not in ("已完成", "已取消"):
                                st.caption(f"🔴 已延期 {t['deadline']}")
                            else:
                                st.caption(f"📅 {t['deadline']}")
                        except:
                            st.caption(f"📅 {t['deadline']}")
                with tc5:
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("✏️", key=f"edit_{t['id']}", help="编辑"):
                            st.session_state["editing_task"] = t
                            st.rerun()
                    with ec2:
                        if st.button("🗑️", key=f"del_{t['id']}", help="删除"):
                            st.session_state["delete_confirm"] = t["id"]
                            st.rerun()
                
                if st.session_state.get("delete_confirm") == t["id"]:
                    st.warning(f"确认删除任务 {t['task_no']} {t['title']}？")
                    dc1, dc2, dc3 = st.columns([1, 1, 4])
                    with dc1:
                        if st.button("确认删除", key=f"confirm_del_{t['id']}", type="primary"):
                            db.delete_task(t["id"])
                            st.session_state.pop("delete_confirm", None)
                            st.success("已删除")
                            st.rerun()
                    with dc2:
                        if st.button("取消", key=f"cancel_del_{t['id']}"):
                            st.session_state.pop("delete_confirm", None)
                            st.rerun()
                
                st.divider()
