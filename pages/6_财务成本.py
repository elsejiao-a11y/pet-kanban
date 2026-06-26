import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 💰 财务成本")

current_user = st.session_state.get("current_user", "阿豪")
costs = db.get_all_costs()

st.markdown("### 产品成本与利润分析")
st.caption("自动计算总成本、毛利和毛利率")

# ===== 新增成本记录 =====
if st.button("➕ 新增成本记录", type="primary", key="add_cost", use_container_width=True):
    st.session_state["show_new_cost"] = True

if st.session_state.get("show_new_cost") or st.session_state.get("editing_cost"):
    is_edit = st.session_state.get("editing_cost") is not None
    edit_data = st.session_state.get("editing_cost")
    
    st.markdown("---")
    with st.form("cost_form", clear_on_submit=True):
        version = st.text_input("产品版本 *", value=edit_data["product_version"] if is_edit else "",
                                placeholder="如：基础款、定位器款、定制款")
        
        st.markdown("#### 成本明细")
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            chest_cost = st.number_input("胸背主体成本（元）", min_value=0.0, 
                                         value=float(edit_data["chest_harness_cost"]) if is_edit else 0.0)
            leash_cost = st.number_input("牵引绳成本（元）", min_value=0.0,
                                        value=float(edit_data["leash_cost"]) if is_edit else 0.0)
            hardware_cost = st.number_input("扣具/五金成本（元）", min_value=0.0,
                                           value=float(edit_data["hardware_cost"]) if is_edit else 0.0)
        with r1c2:
            airtag_cost = st.number_input("AirTag/定位器结构成本（元）", min_value=0.0,
                                         value=float(edit_data["airtag_structure_cost"]) if is_edit else 0.0)
            custom_cost = st.number_input("刻字/印字成本（元）", min_value=0.0,
                                         value=float(edit_data["customization_cost"]) if is_edit else 0.0)
            packaging_cost = st.number_input("包装成本（元）", min_value=0.0,
                                            value=float(edit_data["packaging_cost"]) if is_edit else 0.0)
        with r1c3:
            labor_cost = st.number_input("人工加工费（元）", min_value=0.0,
                                        value=float(edit_data["labor_cost"]) if is_edit else 0.0)
            shipping_cost = st.number_input("单件运费（元）", min_value=0.0,
                                           value=float(edit_data["shipping_cost"]) if is_edit else 0.0)
            other_cost = st.number_input("其他成本（元）", min_value=0.0,
                                        value=float(edit_data["other_cost"]) if is_edit else 0.0)
        
        # 实时计算预览
        total = chest_cost + leash_cost + hardware_cost + airtag_cost + custom_cost + packaging_cost + labor_cost + shipping_cost + other_cost
        
        st.markdown("---")
        st.markdown("#### 售价与利润")
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            suggested_price = st.number_input("建议售价（元）", min_value=0.0,
                                             value=float(edit_data["suggested_price"]) if is_edit else 0.0)
        with r2c2:
            gross_profit = suggested_price - total
            st.metric("预估毛利", f"¥{gross_profit:.2f}")
        with r2c3:
            if suggested_price > 0:
                gross_margin = (gross_profit / suggested_price) * 100
                st.metric("预估毛利率", f"{gross_margin:.1f}%")
            else:
                st.metric("预估毛利率", "N/A")
        
        notes = st.text_area("备注", value=edit_data["notes"] if is_edit else "", height=60)
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("取消", use_container_width=True)
        
        if submitted:
            data = {
                "product_version": version,
                "chest_harness_cost": chest_cost,
                "leash_cost": leash_cost,
                "hardware_cost": hardware_cost,
                "airtag_structure_cost": airtag_cost,
                "customization_cost": custom_cost,
                "packaging_cost": packaging_cost,
                "labor_cost": labor_cost,
                "shipping_cost": shipping_cost,
                "other_cost": other_cost,
                "suggested_price": suggested_price,
                "notes": notes,
            }
            if is_edit:
                db.update_cost(edit_data["id"], data)
                st.success("成本记录已更新！")
                st.session_state.pop("editing_cost", None)
            else:
                db.create_cost(data)
                st.success("成本记录已添加！")
                st.session_state.pop("show_new_cost", None)
            st.rerun()
        if cancelled:
            st.session_state.pop("show_new_cost", None)
            st.session_state.pop("editing_cost", None)
            st.rerun()

# ===== 成本对比与分析 =====
st.markdown("---")

if costs:
    st.markdown("### 📊 版本成本对比")
    
    # 找出最优版本
    best_cost = min(costs, key=lambda x: x["total_cost"])
    best_profit = max(costs, key=lambda x: x["gross_profit"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"💰 **成本最低：** {best_cost['product_version']}（¥{best_cost['total_cost']:.2f}）")
    with col2:
        if best_profit["gross_profit"] > 0:
            st.success(f"📈 **利润最高：** {best_profit['product_version']}（毛利 ¥{best_profit['gross_profit']:.2f}，{best_profit['gross_margin']:.1f}%）")
        else:
            st.warning("⚠️ 暂无版本实现正毛利")
    
    st.markdown("---")
    
    # 各版本详细对比表
    st.markdown("### 📋 各版本详情")
    for c in costs:
        with st.expander(f"📦 {c['product_version']} — 总成本 ¥{c['total_cost']:.2f} | 毛利 ¥{c['gross_profit']:.2f} ({c['gross_margin']:.1f}%)"):
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("**成本明细：**")
                st.markdown(f"- 胸背主体：¥{c['chest_harness_cost']:.2f}")
                st.markdown(f"- 牵引绳：¥{c['leash_cost']:.2f}")
                st.markdown(f"- 扣具/五金：¥{c['hardware_cost']:.2f}")
                st.markdown(f"- AirTag/定位器结构：¥{c['airtag_structure_cost']:.2f}")
                st.markdown(f"- 刻字/印字：¥{c['customization_cost']:.2f}")
                st.markdown(f"- 包装：¥{c['packaging_cost']:.2f}")
                st.markdown(f"- 人工加工：¥{c['labor_cost']:.2f}")
                st.markdown(f"- 运费：¥{c['shipping_cost']:.2f}")
                if c["other_cost"] > 0:
                    st.markdown(f"- 其他：¥{c['other_cost']:.2f}")
                st.markdown(f"- **总成本：¥{c['total_cost']:.2f}**")
            with cc2:
                st.markdown(f"**建议售价：¥{c['suggested_price']:.2f}**")
                profit_color = "🟢" if c["gross_profit"] > 0 else "🔴"
                st.markdown(f"**毛利：{profit_color} ¥{c['gross_profit']:.2f}**")
                st.markdown(f"**毛利率：{profit_color} {c['gross_margin']:.1f}%**")
                if c["gross_margin"] < 30:
                    st.warning("⚠️ 毛利率低于30%，建议调整定价或降低成本")
                elif c["gross_margin"] >= 50:
                    st.success("✅ 毛利率健康")
            if c["notes"]:
                st.caption(f"备注：{c['notes']}")
            
            ec1, ec2 = st.columns([1, 5])
            with ec1:
                if st.button("✏️ 编辑", key=f"edit_cost_{c['id']}"):
                    st.session_state["editing_cost"] = c
                    st.rerun()
            with ec2:
                if st.button("🗑️ 删除", key=f"del_cost_{c['id']}"):
                    db.delete_cost(c["id"])
                    st.success("已删除")
                    st.rerun()
else:
    st.info("暂无成本记录，点击「新增成本记录」开始录入")
    
    # 推荐初始版本
    st.markdown("### 💡 建议先创建以下三个版本：")
    if st.button("🚀 一键初始化三个版本成本模板", type="secondary"):
        db.create_cost({"product_version": "基础款", "chest_harness_cost": 0, "leash_cost": 0, "hardware_cost": 0, "airtag_structure_cost": 0, "customization_cost": 0, "packaging_cost": 0, "labor_cost": 0, "shipping_cost": 0, "other_cost": 0, "suggested_price": 0, "notes": "基础款：胸背+牵引绳套装"})
        db.create_cost({"product_version": "定位器款", "chest_harness_cost": 0, "leash_cost": 0, "hardware_cost": 0, "airtag_structure_cost": 0, "customization_cost": 0, "packaging_cost": 0, "labor_cost": 0, "shipping_cost": 0, "other_cost": 0, "suggested_price": 0, "notes": "含AirTag/定位器安装位"})
        db.create_cost({"product_version": "定制款", "chest_harness_cost": 0, "leash_cost": 0, "hardware_cost": 0, "airtag_structure_cost": 0, "customization_cost": 0, "packaging_cost": 0, "labor_cost": 0, "shipping_cost": 0, "other_cost": 0, "suggested_price": 0, "notes": "含定位器安装位+宠物名定制"})
        st.success("已创建三个版本模板，请填入具体成本数据！")
        st.rerun()
