import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🏭 打样生产")

current_user = st.session_state.get("current_user", "焦蒙豪")
plan_id = st.session_state.get("current_plan_id", 0)
plans = db.get_all_plans()

# ===== 测试重点提醒 =====
with st.expander("📋 样品测试重点检查项", expanded=False):
    st.markdown("""
    - ✅ AirTag 固定是否牢固
    - ✅ 狗是否容易咬到定位器
    - ✅ 牵引受力是否合理
    - ✅ 扣具是否结实
    - ✅ 车缝是否牢固
    - ✅ 是否磨毛
    - ✅ 是否勒脖子
    - ✅ 是否容易穿戴
    - ✅ 水洗后是否变形
    - ✅ 尺码是否准确
    """)

# ===== 选择开发计划和SPU/SKU =====
if not plans:
    st.warning("请先在「产品开发」页面创建开发计划")
else:
    plan_options = {p["id"]: p["name"] for p in plans}
    selected_plan_id = st.selectbox(
        "选择开发计划",
        options=list(plan_options.keys()),
        format_func=lambda x: plan_options[x],
        index=list(plan_options.keys()).index(plan_id) if plan_id in plan_options else 0,
        key="sample_plan_select"
    )
    
    plan_spus = db.get_spus_by_plan(selected_plan_id)
    if plan_spus:
        spu_options = {s["id"]: s["name"] for s in plan_spus}
        selected_spu_id = st.selectbox(
            "选择SPU",
            options=list(spu_options.keys()),
            format_func=lambda x: spu_options[x],
            key="sample_spu_select"
        )
        
        # 获取SPU下的SKU
        skus = db.get_skus_by_spu(selected_spu_id)
        if skus:
            sku_options = {s["id"]: s["name"] for s in skus}
            selected_sku_id = st.selectbox(
                "选择SKU",
                options=list(sku_options.keys()),
                format_func=lambda x: sku_options[x],
                key="sample_sku_select"
            )
        else:
            selected_sku_id = 0
            st.info("该SPU下暂无SKU")
    else:
        selected_spu_id = 0
        st.info("该计划下暂无SPU")
    
    # ===== 获取样品数据 =====
    samples = db.get_samples_by_plan_spu(selected_plan_id, selected_spu_id if selected_spu_id else 0)
    
    # ===== 统计卡片 =====
    if samples:
        s1, s2, s3, s4 = st.columns(4)
        total = len(samples)
        in_progress = len([s for s in samples if s["status"] in ("打样中", "已寄出", "测试中")])
        arrived = len([s for s in samples if s["status"] in ("已收到", "测试中")])
        passed = len([s for s in samples if s["passed"]])
        
        with s1:
            st.metric("总样品数", total)
        with s2:
            st.metric("打样中", in_progress)
        with s3:
            st.metric("已收到/测试中", arrived)
        with s4:
            st.metric("已通过", passed)
    
    # ===== 新增样品 =====
    if st.button("➕ 新增样品", type="primary", key="add_sample", use_container_width=True):
        st.session_state["show_new_sample"] = True
    
    sample_statuses = ["待打样", "打样中", "已寄出", "已收到", "测试中", "需修改", "通过", "淘汰"]
    
    if st.session_state.get("show_new_sample") or st.session_state.get("editing_sample"):
        is_edit = st.session_state.get("editing_sample") is not None
        edit_data = st.session_state.get("editing_sample")
        
        st.markdown("---")
        with st.form("sample_form", clear_on_submit=True):
            st.markdown("### 样品信息")
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                product_version = st.text_input("版本号 *", value=edit_data["product_version"] if is_edit else "", placeholder="如：V1.0")
                supplier_names = db.get_supplier_names()
                supplier_options = [""] + supplier_names if supplier_names else [""]
                supplier = st.selectbox("供应商",
                    options=supplier_options,
                    index=supplier_options.index(edit_data["supplier"]) if is_edit and edit_data["supplier"] in supplier_options else 0)
                sample_content = st.text_area("打样内容", value=edit_data["sample_content"] if is_edit else "", height=80)
            with r1c2:
                status = st.selectbox("状态", sample_statuses,
                    index=sample_statuses.index(edit_data["status"]) if is_edit and edit_data["status"] in sample_statuses else 0)
                owner = st.selectbox("负责人", db.get_user_names(),
                    index=db.get_user_names().index(edit_data["owner"]) if is_edit and edit_data["owner"] in db.get_user_names() else 0)
                expected_date = st.date_input("预计完成时间", value=None)
                actual_date = st.date_input("实际完成时间", value=None)
            
            cost = st.number_input("样品成本（元）", min_value=0.0, value=float(edit_data["cost"]) if is_edit else 0.0)
            
            st.markdown("### 测试与结论")
            test_result = st.text_area("测试结论", value=edit_data["test_result"] if is_edit else "", height=80)
            passed = st.checkbox("是否通过", value=bool(edit_data["passed"]) if is_edit else False)
            modification_notes = st.text_area("修改意见", value=edit_data["modification_notes"] if is_edit else "", height=60)
            next_action = st.text_area("下一步动作", value=edit_data["next_action"] if is_edit else "", height=60)
            notes = st.text_input("备注", value=edit_data["notes"] if is_edit else "")
            
            c1, c2, c3 = st.columns([1, 1, 3])
            with c1:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with c2:
                cancelled = st.form_submit_button("取消", use_container_width=True)
            
            if submitted:
                data = {
                    "plan_id": selected_plan_id, "spu_id": selected_spu_id if selected_spu_id else 0,
                    "sku_id": selected_sku_id if selected_sku_id else 0,
                    "product_version": product_version, "supplier": supplier,
                    "sample_content": sample_content, "cost": cost,
                    "expected_date": expected_date.strftime("%Y-%m-%d") if expected_date else "",
                    "actual_date": actual_date.strftime("%Y-%m-%d") if actual_date else "",
                    "status": status, "test_result": test_result,
                    "passed": passed, "modification_notes": modification_notes,
                    "owner": owner, "next_action": next_action, "notes": notes,
                }
                if is_edit:
                    db.update_sample(edit_data["id"], data)
                    st.success(f"样品 {edit_data['sample_no']} 已更新！")
                    st.session_state.pop("editing_sample", None)
                else:
                    new_id = db.create_sample(data)
                    st.success("样品已添加！")
                    st.session_state.pop("show_new_sample", None)
                st.rerun()
            
            if cancelled:
                st.session_state.pop("show_new_sample", None)
                st.session_state.pop("editing_sample", None)
                st.rerun()
    
    # ===== 样品列表 =====
    st.markdown("---")
    
    if not samples:
        st.info("暂无样品记录，点击「新增样品」开始录入")
    else:
        st.markdown("### 📦 样品列表")
        
        for s in samples:
            status_colors = {
                "待打样": "#95A5A6", "打样中": "#3498DB", "已寄出": "#2980B9",
                "已收到": "#27AE60", "测试中": "#F39C12", "需修改": "#E67E22",
                "通过": "#2ECC71", "淘汰": "#BDC3C7",
            }
            color = status_colors.get(s["status"], "#999")
            
            with st.container():
                sc1, sc2, sc3 = st.columns([3, 1.5, 1])
                with sc1:
                    pass_badge = "✅" if s["passed"] else ("❌" if s["status"] == "淘汰" else "")
                    st.markdown(f"**{s['sample_no']} {s['product_version']}** {pass_badge}")
                    st.caption(f"供应商: {s['supplier'] or '未设置'} | 💰 ¥{s['cost']} | 👤 {s['owner']}")
                    if s["sample_content"]:
                        st.caption(f"📝 {s['sample_content'][:80]}")
                with sc2:
                    st.markdown(f'<span style="color:{color};font-weight:bold">● {s["status"]}</span>', unsafe_allow_html=True)
                    st.caption(f"预计: {s['expected_date'] or '未定'}")
                    st.caption(f"实际: {s['actual_date'] or '未到'}")
                with sc3:
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("✏️", key=f"edit_samp_{s['id']}"):
                            st.session_state["editing_sample"] = s
                            st.rerun()
                    with ec2:
                        if st.button("🗑️", key=f"del_samp_{s['id']}"):
                            st.session_state["delete_sample_confirm"] = s["id"]
                            st.rerun()
                
                if st.session_state.get("delete_sample_confirm") == s["id"]:
                    st.warning(f"确认删除样品 {s['sample_no']}？")
                    if st.button("确认删除", type="primary", key=f"confirm_del_samp_{s['id']}"):
                        db.delete_sample(s["id"])
                        st.session_state.pop("delete_sample_confirm", None)
                        st.success("已删除")
                        st.rerun()
                
                if s["test_result"]:
                    st.markdown(f"> 📋 **测试结论：** {s['test_result']}")
                if s["modification_notes"]:
                    st.markdown(f"> 🔧 **修改意见：** {s['modification_notes']}")
                if s["next_action"]:
                    st.markdown(f"> ➡️ **下一步：** {s['next_action']}")
                st.divider()
