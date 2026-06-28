import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 💰 财务成本")

current_user = st.session_state.get("current_user", "焦蒙豪")
plan_id = st.session_state.get("current_plan_id", 0)
plans = db.get_all_plans()

# ===== 选择开发计划 → SPU → SKU =====
if not plans:
    st.warning("请先在「产品开发」页面创建开发计划")
else:
    plan_options = {p["id"]: p["name"] for p in plans}
    selected_plan_id = st.selectbox(
        "选择开发计划",
        options=list(plan_options.keys()),
        format_func=lambda x: plan_options[x],
        index=list(plan_options.keys()).index(plan_id) if plan_id in plan_options else 0,
        key="cost_plan_select"
    )
    
    plan_spus = db.get_spus_by_plan(selected_plan_id)
    if plan_spus:
        spu_options = {s["id"]: s["name"] for s in plan_spus}
        selected_spu_id = st.selectbox(
            "选择SPU",
            options=list(spu_options.keys()),
            format_func=lambda x: spu_options[x],
            key="cost_spu_select"
        )
        
        skus = db.get_skus_by_spu(selected_spu_id)
        if skus:
            sku_options = {s["id"]: s["name"] for s in skus}
            selected_sku_id = st.selectbox(
                "选择SKU",
                options=list(sku_options.keys()),
                format_func=lambda x: sku_options[x],
                key="cost_sku_select"
            )
            
            sku = db.get_sku(selected_sku_id)
            if sku:
                st.markdown(f"**预估售价：** ¥{sku['estimated_price']}")
        else:
            selected_sku_id = 0
            st.info("该SPU下暂无SKU")
    else:
        selected_spu_id = 0
        st.info("该计划下暂无SPU")
        selected_sku_id = 0

# ===== 获取成本明细 =====
cost_items = db.get_cost_items(selected_plan_id, selected_spu_id, selected_sku_id)

# ===== 初始化session_state管理成本项 =====
if "cost_items_temp" not in st.session_state:
    st.session_state["cost_items_temp"] = cost_items

# ===== 总成本计算 =====
total_cost = sum(item["subtotal"] for item in st.session_state["cost_items_temp"])

st.markdown("---")
st.markdown(f"### 📊 成本明细表（总成本：¥{total_cost:.2f}）")

# ===== 成本项列表 =====
if st.session_state["cost_items_temp"]:
    for i, item in enumerate(st.session_state["cost_items_temp"]):
        with st.container():
            c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
            with c1:
                st.markdown(f"**{item['name']}**")
                st.caption(f"类型: {item['category']}")
            with c2:
                st.markdown(f"数量: {item['quantity']}{item.get('unit', '个')}")
            with c3:
                st.markdown(f"单价: ¥{item['unit_price']:.2f}")
            with c4:
                st.markdown(f"**小计: ¥{item['subtotal']:.2f}**")
            with c5:
                if st.button("⬆️", key=f"up_{item['id']}_{i}", help="上移", disabled=i == 0):
                    st.session_state["cost_items_temp"].insert(i-1, st.session_state["cost_items_temp"].pop(i))
                    st.rerun()
            with c6:
                if st.button("⬇️", key=f"down_{item['id']}_{i}", help="下移", disabled=i == len(st.session_state["cost_items_temp"])-1):
                    st.session_state["cost_items_temp"].insert(i+1, st.session_state["cost_items_temp"].pop(i))
                    st.rerun()
            
            b1, b2 = st.columns([1, 5])
            with b1:
                if st.button("✏️ 编辑", key=f"edit_cost_{item['id']}"):
                    st.session_state["editing_cost_item"] = item
                if st.button("🗑️", key=f"del_cost_{item['id']}"):
                    # 从session_state删除
                    st.session_state["cost_items_temp"] = [x for x in st.session_state["cost_items_temp"] if x.get("id") != item["id"] or x.get("temp_id") != item.get("temp_id")]
                    # 从数据库删除
                    if item.get("id"):
                        db.delete_cost_item(item["id"])
                    st.rerun()
            st.divider()

# ===== 新增成本项 =====
if st.button("➕ 新增成本项", type="primary"):
    st.session_state["show_new_cost_item"] = True

# 默认成本项建议
default_items = [
    ("半成品成本", "物料"), ("塑料袋", "包装"), ("说明书", "包装"),
    ("纸箱", "包装"), ("定位器", "配件"), ("刻字成本", "服务"),
    ("LOGO印刷成本", "服务"), ("包装成本", "包装"), ("运费", "物流"),
    ("平台扣点", "营销"), ("推广预估", "营销"), ("售后预估", "服务"),
    ("其他成本", "其他"),
]

# 快速添加默认项
with st.expander("💡 快速添加默认成本项"):
    cols = st.columns(4)
    for i, (name, category) in enumerate(default_items):
        with cols[i % 4]:
            if st.button(f"+ {name}", key=f"quick_add_{name}"):
                # 检查是否已存在
                exists = any(item["name"] == name for item in st.session_state["cost_items_temp"])
                if not exists:
                    new_item = {
                        "temp_id": f"temp_{len(st.session_state['cost_items_temp']) + 1}",
                        "name": name,
                        "category": category,
                        "quantity": 1,
                        "unit_price": 0,
                        "subtotal": 0,
                    }
                    st.session_state["cost_items_temp"].append(new_item)
                    st.rerun()

if st.session_state.get("show_new_cost_item") or st.session_state.get("editing_cost_item"):
    is_edit = st.session_state.get("editing_cost_item") is not None
    edit_data = st.session_state.get("editing_cost_item")
    
    st.markdown("---")
    st.markdown(f"### {'✏️ 编辑成本项' if is_edit else '➕ 新增成本项'}")
    
    with st.form("cost_item_form", clear_on_submit=True):
        name = st.text_input("成本项名称 *", value=edit_data["name"] if is_edit else "")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            category = st.selectbox("类别", ["物料", "包装", "配件", "服务", "物流", "营销", "其他"],
                index=["物料", "包装", "配件", "服务", "物流", "营销", "其他"].index(edit_data["category"]) if is_edit and edit_data["category"] in ["物料", "包装", "配件", "服务", "物流", "营销", "其他"] else 0)
        with c2:
            quantity = st.number_input("数量", min_value=0.1, value=float(edit_data["quantity"]) if is_edit else 1.0)
        with c3:
            unit_price = st.number_input("单价（元）", min_value=0.0, value=float(edit_data["unit_price"]) if is_edit else 0.0)
        
        notes = st.text_input("备注", value=edit_data.get("notes","") if is_edit else "")
        
        subtotal = quantity * unit_price
        st.markdown(f"**小计：¥{subtotal:.2f}**")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("取消", use_container_width=True)
        
        if submitted:
            data = {
                "name": name, "category": category, "quantity": quantity,
                "unit_price": unit_price, "subtotal": subtotal, "notes": notes,
            }
            if is_edit:
                # 更新session_state
                for i, item in enumerate(st.session_state["cost_items_temp"]):
                    if item.get("id") == edit_data.get("id") or item.get("temp_id") == edit_data.get("temp_id"):
                        data["plan_id"] = selected_plan_id
                        data["spu_id"] = selected_spu_id
                        data["sku_id"] = selected_sku_id
                        if item.get("id"):
                            db.update_cost_item(item["id"], data)
                        st.session_state["cost_items_temp"][i] = {**item, **data}
                        break
                st.success("成本项已更新！")
                st.session_state.pop("editing_cost_item", None)
            else:
                data["plan_id"] = selected_plan_id
                data["spu_id"] = selected_spu_id
                data["sku_id"] = selected_sku_id
                new_id = db.create_cost_item(data)
                st.session_state["cost_items_temp"].append({**data, "id": new_id, "temp_id": f"temp_{new_id}"})
                st.success("成本项已添加！")
                st.session_state.pop("show_new_cost_item", None)
            st.rerun()
        
        if cancelled:
            st.session_state.pop("show_new_cost_item", None)
            st.session_state.pop("editing_cost_item", None)
            st.rerun()

# ===== 利润模拟 =====
st.markdown("---")
st.markdown("### 📈 利润模拟")

suggested_price = st.number_input("建议售价（元）", min_value=0.0, value=float(sku["estimated_price"]) if sku else 0.0, key="sim_price")

if st.session_state["cost_items_temp"]:
    gross_profit = suggested_price - total_cost
    gross_margin = (gross_profit / suggested_price * 100) if suggested_price > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("总成本", f"¥{total_cost:.2f}")
    with c2:
        st.metric("毛利", f"¥{gross_profit:.2f}", delta_color="normal" if gross_profit > 0 else "inverse")
    with c3:
        st.metric("毛利率", f"{gross_margin:.1f}%", delta_color="normal" if gross_margin > 30 else "inverse")
    
    if gross_margin < 30:
        st.warning("⚠️ 毛利率低于30%，建议调整定价或降低成本")
    elif gross_margin >= 50:
        st.success("✅ 毛利率健康（≥50%）")
    
    # 保本售价
    break_even = total_cost / 0.3 if total_cost > 0 else 0  # 假设30%毛利率
    st.markdown(f"**保本售价（30%毛利率）：** ¥{break_even:.2f}")
    
    # 多价位模拟
    st.markdown("#### 多价位利润模拟")
    prices = [suggested_price * r for r in [0.8, 0.9, 1.0, 1.1, 1.2]]
    sim_cols = st.columns(len(prices))
    for col, price in zip(sim_cols, prices):
        profit = price - total_cost
        margin = (profit / price * 100) if price > 0 else 0
        with col:
            st.markdown(f"**¥{price:.0f}**")
            st.caption(f"毛利: ¥{profit:.0f}")
            st.caption(f"利率: {margin:.0f}%")
else:
    st.info("添加成本项后即可计算利润")

# ===== 批量保存到数据库 =====
st.markdown("---")
if st.button("💾 批量保存所有成本项", type="primary", use_container_width=True):
    for item in st.session_state["cost_items_temp"]:
        if item.get("id"):
            db.update_cost_item(item["id"], {
                "name": item["name"], "category": item["category"],
                "quantity": item["quantity"], "unit_price": item["unit_price"],
                "subtotal": item["subtotal"], "notes": item.get("notes", "")
            })
        else:
            db.create_cost_item({
                "plan_id": selected_plan_id, "spu_id": selected_spu_id, "sku_id": selected_sku_id,
                "name": item["name"], "category": item["category"],
                "quantity": item["quantity"], "unit_price": item["unit_price"],
                "subtotal": item["subtotal"], "source": "手动", "notes": item.get("notes", "")
            })
    st.success("所有成本项已保存！")
