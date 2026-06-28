import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 📦 产品开发")

plan_id = st.session_state.get("current_plan_id", 0)
plans = db.get_all_plans()

# ===== 三个Tab =====
tab1, tab2, tab3 = st.tabs(["📋 开发计划", "🏷️ SPU管理", "📊 SKU与零部件"])

# ===== Tab 1: 开发计划 =====
with tab1:
    st.markdown("### 开发计划列表")
    
    # 显示所有计划
    all_plans = db.get_all_plans()
    if all_plans:
        for plan in all_plans:
            with st.expander(f"{plan['name']} ({plan['status']})"):
                st.markdown(f"**描述：** {plan['description'] or '无'}")
                st.markdown(f"**负责人：** {plan['owner']} | **状态：** {plan['status']}")
                st.markdown(f"**开始日期：** {plan['start_date'] or '未设置'} | **目标日期：** {plan['target_date'] or '未设置'}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✏️ 编辑", key=f"edit_plan_{plan['id']}"):
                        st.session_state["editing_plan"] = plan
                with col2:
                    if st.button("🗑️ 删除", key=f"del_plan_{plan['id']}"):
                        st.session_state["delete_plan_confirm"] = plan["id"]
                with col3:
                    if st.button("📦 查看SPU", key=f"view_spu_{plan['id']}"):
                        st.session_state["current_plan_id"] = plan["id"]
                        st.rerun()
                
                if st.session_state.get("delete_plan_confirm") == plan["id"]:
                    st.warning(f"确认删除计划「{plan['name']}」？此操作不可恢复！")
                    if st.button("确认删除", type="primary", key=f"confirm_del_plan_{plan['id']}"):
                        db.delete_plan(plan["id"])
                        st.session_state.pop("delete_plan_confirm", None)
                        st.success("已删除")
                        st.rerun()
    else:
        st.info("暂无开发计划，请新增")
    
    # 新增/编辑计划
    if st.button("➕ 新增开发计划", type="primary"):
        st.session_state["show_new_plan"] = True
    
    if st.session_state.get("show_new_plan") or st.session_state.get("editing_plan"):
        is_edit = st.session_state.get("editing_plan") is not None
        edit_data = st.session_state.get("editing_plan")
        
        st.markdown("---")
        st.markdown(f"### {'✏️ 编辑计划' if is_edit else '➕ 新增开发计划'}")
        
        with st.form("plan_form", clear_on_submit=True):
            name = st.text_input("计划名称 *", value=edit_data["name"] if is_edit else "")
            description = st.text_area("描述", value=edit_data["description"] if is_edit else "", height=80)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                owner = st.selectbox("负责人", db.get_user_names(),
                    index=db.get_user_names().index(edit_data["owner"]) if is_edit and edit_data["owner"] in db.get_user_names() else 0)
            with c2:
                status = st.selectbox("状态", ["进行中", "已完成", "已暂停", "已取消"],
                    index=["进行中", "已完成", "已暂停", "已取消"].index(edit_data["status"]) if is_edit and edit_data["status"] in ["进行中", "已完成", "已暂停", "已取消"] else 0)
            with c3:
                target_date = st.date_input("目标完成日期", value=None)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with col2:
                cancelled = st.form_submit_button("取消", use_container_width=True)
            
            if submitted:
                data = {
                    "name": name, "description": description, "owner": owner,
                    "status": status, "target_date": target_date.strftime("%Y-%m-%d") if target_date else ""
                }
                if is_edit:
                    db.update_plan(edit_data["id"], data)
                    st.success("计划已更新！")
                    st.session_state.pop("editing_plan", None)
                else:
                    db.create_plan(data)
                    st.success("计划已创建！")
                    st.session_state.pop("show_new_plan", None)
                st.rerun()
            
            if cancelled:
                st.session_state.pop("show_new_plan", None)
                st.session_state.pop("editing_plan", None)
                st.rerun()

# ===== Tab 2: SPU管理 =====
with tab2:
    st.markdown("### SPU管理（标准产品单元）")
    
    if not plans:
        st.warning("请先创建开发计划")
    else:
        # 选择计划
        plan_options = {p["id"]: p["name"] for p in plans}
        selected_plan_id = st.selectbox(
            "选择开发计划",
            options=list(plan_options.keys()),
            format_func=lambda x: plan_options[x],
            index=list(plan_options.keys()).index(plan_id) if plan_id in plan_options else 0,
            key="spu_plan_select"
        )
        
        # 显示该计划的SPU
        spus = db.get_spus_by_plan(selected_plan_id)
        
        # 产品大类选项
        categories = ["胸背牵引", "定位器配件", "定制服务", "包装配件", "其他"]
        stages = ["概念", "规划", "设计", "打样", "测试", "上市"]
        
        if spus:
            for spu in spus:
                with st.expander(f"{spu['name']} ({spu['stage']})"):
                    st.markdown(f"**类别：** {spu['category']} | **定位：** {spu['positioning'] or '未设置'}")
                    st.markdown(f"**目标人群：** {spu['target_audience'] or '未设置'}")
                    st.markdown(f"**核心卖点：** {spu['selling_points'] or '未设置'}")
                    st.markdown(f"**负责人：** {spu['owner']}")
                    if spu.get("notes"):
                        st.caption(f"备注：{spu['notes']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ 编辑", key=f"edit_spu_{spu['id']}"):
                            st.session_state["editing_spu"] = spu
                    with col2:
                        if st.button("📦 SKU管理", key=f"manage_sku_{spu['id']}"):
                            st.session_state["current_spu_id"] = spu["id"]
                            st.rerun()
                    with col3:
                        if st.button("🗑️ 删除", key=f"del_spu_{spu['id']}"):
                            st.session_state["delete_spu_confirm"] = spu["id"]
                    
                    if st.session_state.get("delete_spu_confirm") == spu["id"]:
                        st.warning(f"确认删除SPU「{spu['name']}」？此操作不可恢复！")
                        if st.button("确认删除", type="primary", key=f"confirm_del_spu_{spu['id']}"):
                            db.delete_spu(spu["id"])
                            st.session_state.pop("delete_spu_confirm", None)
                            st.success("已删除")
                            st.rerun()
        else:
            st.info("该计划下暂无SPU，请新增")
        
        # 新增SPU
        if st.button("➕ 新增SPU", type="primary"):
            st.session_state["show_new_spu"] = True
        
        if st.session_state.get("show_new_spu") or st.session_state.get("editing_spu"):
            is_edit = st.session_state.get("editing_spu") is not None
            edit_data = st.session_state.get("editing_spu")
            
            st.markdown("---")
            st.markdown(f"### {'✏️ 编辑SPU' if is_edit else '➕ 新增SPU'}")
            
            with st.form("spu_form", clear_on_submit=True):
                name = st.text_input("SPU名称 *", value=edit_data["name"] if is_edit else "")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    category = st.selectbox("产品大类", categories,
                        index=categories.index(edit_data["category"]) if is_edit and edit_data["category"] in categories else 0)
                with c2:
                    stage = st.selectbox("当前阶段", stages,
                        index=stages.index(edit_data["stage"]) if is_edit and edit_data["stage"] in stages else 0)
                with c3:
                    owner = st.selectbox("负责人", db.get_user_names(),
                        index=db.get_user_names().index(edit_data["owner"]) if is_edit and edit_data["owner"] in db.get_user_names() else 0)
                
                positioning = st.text_input("产品定位", value=edit_data["positioning"] if is_edit else "")
                target_audience = st.text_input("目标人群", value=edit_data["target_audience"] if is_edit else "")
                selling_points = st.text_area("核心卖点", value=edit_data["selling_points"] if is_edit else "", height=60)
                notes = st.text_area("备注", value=edit_data["notes"] if is_edit else "", height=60)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
                with col2:
                    cancelled = st.form_submit_button("取消", use_container_width=True)
                
                if submitted:
                    data = {
                        "plan_id": selected_plan_id, "name": name, "category": category,
                        "positioning": positioning, "target_audience": target_audience,
                        "selling_points": selling_points, "stage": stage, "owner": owner, "notes": notes
                    }
                    if is_edit:
                        db.update_spu(edit_data["id"], data)
                        st.success("SPU已更新！")
                        st.session_state.pop("editing_spu", None)
                    else:
                        db.create_spu(data)
                        st.success("SPU已创建！")
                        st.session_state.pop("show_new_spu", None)
                    st.rerun()
                
                if cancelled:
                    st.session_state.pop("show_new_spu", None)
                    st.session_state.pop("editing_spu", None)
                    st.rerun()

# ===== Tab 3: SKU与零部件 =====
with tab3:
    st.markdown("### SKU与零部件管理")
    
    if not plans:
        st.warning("请先创建开发计划")
    else:
        # 选择计划
        plan_options = {p["id"]: p["name"] for p in plans}
        selected_plan_id = st.selectbox(
            "选择开发计划",
            options=list(plan_options.keys()),
            format_func=lambda x: plan_options[x],
            index=list(plan_options.keys()).index(plan_id) if plan_id in plan_options else 0,
            key="sku_plan_select"
        )
        
        # 选择SPU
        plan_spus = db.get_spus_by_plan(selected_plan_id)
        if not plan_spus:
            st.info("该计划下暂无SPU，请先添加SPU")
        else:
            spu_options = {s["id"]: s["name"] for s in plan_spus}
            selected_spu_id = st.selectbox(
                "选择SPU",
                options=list(spu_options.keys()),
                format_func=lambda x: spu_options[x],
                index=0,
                key="sku_spu_select"
            )
            
            # 显示该SPU下的SKU
            skus = db.get_skus_by_spu(selected_spu_id)
            
            if skus:
                for sku in skus:
                    components = db.get_components_by_sku(sku["id"])
                    with st.expander(f"{sku['name']} ({sku['status']}) - ¥{sku['estimated_price']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**颜色：** {sku['color'] or '无'}")
                            st.markdown(f"**尺码：** {sku['size'] or '无'}")
                        with col2:
                            st.markdown(f"**款式：** {sku['style'] or '无'}")
                            features = []
                            if sku["has_engraving"]: features.append("✓ 支持刻字")
                            if sku["has_locator_port"]: features.append("✓ 定位器接口")
                            if sku["has_locator"]: features.append("✓ 含定位器")
                            st.markdown("**特性：** " + " | ".join(features) if features else "无")
                        with col3:
                            st.markdown(f"**预估售价：** ¥{sku['estimated_price']}")
                            st.markdown(f"**状态：** {sku['status']}")
                        
                        # 零部件列表
                        st.markdown("#### 零部件明细")
                        if components:
                            for comp in components:
                                st.markdown(f"- {comp['name']} | 类型: {comp['type']} | 数量: {comp['quantity']}{comp['unit']} | 单价: ¥{comp['unit_price']} | 供应商: {comp['supplier'] or '未设置'}")
                        else:
                            st.caption("暂无零部件")
                        
                        # 操作按钮
                        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
                        with bcol1:
                            if st.button("✏️ 编辑SKU", key=f"edit_sku_{sku['id']}"):
                                st.session_state["editing_sku"] = sku
                        with bcol2:
                            if st.button("➕ 零部件", key=f"add_comp_{sku['id']}"):
                                st.session_state["adding_component_to_sku"] = sku["id"]
                        with bcol3:
                            if st.button("📋 复制成本项", key=f"copy_cost_{sku['id']}"):
                                # 复制到成本明细表
                                for comp in components:
                                    db.create_cost_item({
                                        "plan_id": selected_plan_id, "spu_id": selected_spu_id,
                                        "sku_id": sku["id"], "name": comp["name"],
                                        "category": "物料", "quantity": comp["quantity"],
                                        "unit_price": comp["unit_price"], "source": "从零部件导入"
                                    })
                                st.success("已复制到成本明细！")
                        with bcol4:
                            if st.button("🗑️ 删除SKU", key=f"del_sku_{sku['id']}"):
                                st.session_state["delete_sku_confirm"] = sku["id"]
                        
                        if st.session_state.get("delete_sku_confirm") == sku["id"]:
                            st.warning(f"确认删除SKU「{sku['name']}」？此操作不可恢复！")
                            if st.button("确认删除", type="primary", key=f"confirm_del_sku_{sku['id']}"):
                                db.delete_sku(sku["id"])
                                st.session_state.pop("delete_sku_confirm", None)
                                st.success("已删除")
                                st.rerun()
            else:
                st.info("该SPU下暂无SKU，请新增")
            
            # 新增SKU按钮
            if st.button("➕ 新增SKU", type="primary"):
                st.session_state["show_new_sku"] = True
            
            # 新增/编辑SKU表单
            if st.session_state.get("show_new_sku") or st.session_state.get("editing_sku"):
                is_edit = st.session_state.get("editing_sku") is not None
                edit_data = st.session_state.get("editing_sku")
                
                st.markdown("---")
                st.markdown(f"### {'✏️ 编辑SKU' if is_edit else '➕ 新增SKU'}")
                
                with st.form("sku_form", clear_on_submit=True):
                    name = st.text_input("SKU名称 *", value=edit_data["name"] if is_edit else "")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        color = st.text_input("颜色", value=edit_data["color"] if is_edit else "")
                        size = st.text_input("尺码", value=edit_data["size"] if is_edit else "")
                    with c2:
                        style = st.text_input("款式", value=edit_data["style"] if is_edit else "")
                        estimated_price = st.number_input("预估售价（元）", min_value=0.0,
                            value=float(edit_data["estimated_price"]) if is_edit else 0.0)
                    with c3:
                        status = st.selectbox("状态", ["开发中", "已定型", "已上市", "已停产"],
                            index=["开发中", "已定型", "已上市", "已停产"].index(edit_data["status"]) if is_edit and edit_data["status"] in ["开发中", "已定型", "已上市", "已停产"] else 0)
                    
                    has_engraving = st.checkbox("支持刻字", value=bool(edit_data["has_engraving"]) if is_edit else False)
                    has_locator_port = st.checkbox("支持定位器接口", value=bool(edit_data["has_locator_port"]) if is_edit else False)
                    has_locator = st.checkbox("含定位器", value=bool(edit_data["has_locator"]) if is_edit else False)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
                    with col2:
                        cancelled = st.form_submit_button("取消", use_container_width=True)
                    
                    if submitted:
                        data = {
                            "spu_id": selected_spu_id, "name": name, "color": color,
                            "size": size, "style": style, "has_engraving": has_engraving,
                            "has_locator_port": has_locator_port, "has_locator": has_locator,
                            "estimated_price": estimated_price, "status": status
                        }
                        if is_edit:
                            db.update_sku(edit_data["id"], data)
                            st.success("SKU已更新！")
                            st.session_state.pop("editing_sku", None)
                        else:
                            db.create_sku(data)
                            st.success("SKU已创建！")
                            st.session_state.pop("show_new_sku", None)
                        st.rerun()
                    
                    if cancelled:
                        st.session_state.pop("show_new_sku", None)
                        st.session_state.pop("editing_sku", None)
                        st.rerun()
            
            # 新增零部件表单
            if st.session_state.get("adding_component_to_sku"):
                sku_id = st.session_state["adding_component_to_sku"]
                sku = db.get_sku(sku_id)
                
                st.markdown("---")
                st.markdown(f"### ➕ 新增零部件（所属SKU: {sku['name']}）")
                
                component_types = ["半成品", "塑料袋", "说明书", "纸箱", "定位器", "LOGO印刷", "刻字服务", "五金件", "织带", "其他"]
                
                with st.form("component_form", clear_on_submit=True):
                    name = st.text_input("零部件名称 *")
                    comp_type = st.selectbox("类型", component_types)
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        quantity = st.number_input("数量", min_value=0.1, value=1.0)
                        unit = st.text_input("单位", value="个")
                    with c2:
                        unit_price = st.number_input("单价（元）", min_value=0.0, value=0.0)
                        supplier = st.text_input("供应商", value="")
                    with c3:
                        notes = st.text_area("备注", height=80)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
                    with col2:
                        cancelled = st.form_submit_button("取消", use_container_width=True)
                    
                    if submitted:
                        db.create_component({
                            "sku_id": sku_id, "name": name, "type": comp_type,
                            "quantity": quantity, "unit": unit, "unit_price": unit_price,
                            "supplier": supplier, "notes": notes
                        })
                        st.success("零部件已添加！")
                        st.session_state.pop("adding_component_to_sku", None)
                        st.rerun()
                    
                    if cancelled:
                        st.session_state.pop("adding_component_to_sku", None)
                        st.rerun()
