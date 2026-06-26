import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🏢 供应商管理")

current_user = st.session_state.get("current_user", "阿豪")
suppliers = db.get_all_suppliers()

supplier_types = ["全部", "胸背工厂", "织带供应商", "扣具供应商", "五金供应商", "硅胶件供应商", "包装供应商", "定制印字供应商", "其他"]
coop_statuses = ["全部", "未联系", "已联系", "等报价", "已报价", "已打样", "可合作", "不合适"]

# ===== 筛选 =====
fc1, fc2 = st.columns(2)
with fc1:
    filter_type = st.selectbox("供应商类型", supplier_types, key="sup_type")
with fc2:
    filter_status = st.selectbox("合作状态", coop_statuses, key="sup_status")

filtered = suppliers
if filter_type != "全部":
    filtered = [s for s in filtered if s["type"] == filter_type]
if filter_status != "全部":
    filtered = [s for s in filtered if s["cooperation_status"] == filter_status]

st.markdown(f"**共 {len(filtered)} 个供应商**")

# ===== 新增供应商 =====
if st.button("➕ 新增供应商", type="primary", key="add_sup", use_container_width=True):
    st.session_state["show_new_sup"] = True

if st.session_state.get("show_new_sup") or st.session_state.get("editing_sup"):
    is_edit = st.session_state.get("editing_sup") is not None
    edit_data = st.session_state.get("editing_sup")
    
    st.markdown("---")
    with st.form("sup_form", clear_on_submit=True):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            name = st.text_input("供应商名称 *", value=edit_data["name"] if is_edit else "")
            sup_type = st.selectbox("类型", supplier_types[1:],
                                   index=supplier_types[1:].index(edit_data["type"]) if is_edit and edit_data["type"] in supplier_types[1:] else 0)
            contact_person = st.text_input("联系人", value=edit_data["contact_person"] if is_edit else "")
            contact_info = st.text_input("联系方式", value=edit_data["contact_info"] if is_edit else "")
            location = st.text_input("所在地", value=edit_data["location"] if is_edit else "")
        with r1c2:
            products = st.text_input("可做产品", value=edit_data["products"] if is_edit else "")
            quote_price = st.text_input("报价", value=edit_data["quote_price"] if is_edit else "")
            moq = st.text_input("起订量", value=edit_data["moq"] if is_edit else "")
            sample_cost = st.number_input("打样费（元）", min_value=0.0, value=float(edit_data["sample_cost"]) if is_edit else 0.0)
            cooperation_status = st.selectbox("合作状态", coop_statuses[1:],
                                             index=coop_statuses[1:].index(edit_data["cooperation_status"]) if is_edit and edit_data["cooperation_status"] in coop_statuses[1:] else 0)
        
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            sample_lead_time = st.text_input("打样周期", value=edit_data["sample_lead_time"] if is_edit else "", placeholder="如：7-10天")
            production_lead_time = st.text_input("大货周期", value=edit_data["production_lead_time"] if is_edit else "", placeholder="如：15-30天")
        
        advantages = st.text_area("优势", value=edit_data["advantages"] if is_edit else "", height=60)
        risks = st.text_area("风险", value=edit_data["risks"] if is_edit else "", height=60)
        notes = st.text_input("备注", value=edit_data["notes"] if is_edit else "")
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("取消", use_container_width=True)
        
        if submitted:
            data = {
                "name": name, "type": sup_type, "contact_person": contact_person,
                "contact_info": contact_info, "location": location,
                "products": products, "quote_price": quote_price, "moq": moq,
                "sample_cost": sample_cost, "sample_lead_time": sample_lead_time,
                "production_lead_time": production_lead_time,
                "advantages": advantages, "risks": risks,
                "cooperation_status": cooperation_status, "notes": notes,
            }
            if is_edit:
                db.update_supplier(edit_data["id"], data)
                st.success("供应商已更新！")
                st.session_state.pop("editing_sup", None)
            else:
                db.create_supplier(data)
                st.success("供应商已添加！")
                st.session_state.pop("show_new_sup", None)
            st.rerun()
        if cancelled:
            st.session_state.pop("show_new_sup", None)
            st.session_state.pop("editing_sup", None)
            st.rerun()

# ===== 供应商列表 =====
st.markdown("---")

if not filtered:
    st.info("暂无供应商数据")
else:
    # 按合作状态分组
    status_order = ["可合作", "已打样", "已报价", "等报价", "已联系", "未联系", "不合适"]
    for status_name in status_order:
        status_sups = [s for s in filtered if s["cooperation_status"] == status_name]
        if not status_sups:
            continue
        
        status_colors = {
            "可合作": "🟢", "已打样": "🔵", "已报价": "🟡",
            "等报价": "🟠", "已联系": "⚪", "未联系": "⚫", "不合适": "❌",
        }
        icon = status_colors.get(status_name, "⚪")
        st.markdown(f"#### {icon} {status_name}（{len(status_sups)}）")
        
        for s in status_sups:
            with st.container():
                sc1, sc2, sc3 = st.columns([3, 1.5, 1])
                with sc1:
                    st.markdown(f"**{s['name']}**")
                    meta = []
                    meta.append(f"📁 {s['type']}")
                    if s["location"]:
                        meta.append(f"📍 {s['location']}")
                    if s["contact_person"]:
                        meta.append(f"👤 {s['contact_person']}")
                    st.caption(" | ".join(meta))
                    if s["products"]:
                        st.caption(f"🏷️ 可做: {s['products']}")
                with sc2:
                    if s["quote_price"]:
                        st.caption(f"💰 报价: {s['quote_price']}")
                    if s["moq"]:
                        st.caption(f"📦 起订量: {s['moq']}")
                    if s["sample_cost"]:
                        st.caption(f"🔧 打样费: ¥{s['sample_cost']}")
                    st.caption(f"⏱️ 打样: {s['sample_lead_time'] or '未定'} | 大货: {s['production_lead_time'] or '未定'}")
                with sc3:
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("✏️", key=f"edit_sup_{s['id']}"):
                            st.session_state["editing_sup"] = s
                            st.rerun()
                    with ec2:
                        if st.button("🗑️", key=f"del_sup_{s['id']}"):
                            db.delete_supplier(s["id"])
                            st.success("已删除")
                            st.rerun()
                
                info_parts = []
                if s["advantages"]:
                    info_parts.append(f"✅ 优势: {s['advantages']}")
                if s["risks"]:
                    info_parts.append(f"⚠️ 风险: {s['risks']}")
                if s["contact_info"]:
                    info_parts.append(f"📞 {s['contact_info']}")
                if info_parts:
                    st.markdown("> " + " | ".join(info_parts))
                st.divider()
