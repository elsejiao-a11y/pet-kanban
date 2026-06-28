import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🔬 竞品分析")

plan_id = st.session_state.get("current_plan_id", 0)
plans = db.get_all_plans()

# ===== 选择开发计划和SPU =====
if not plans:
    st.warning("请先在「产品开发」页面创建开发计划")
else:
    plan_options = {p["id"]: p["name"] for p in plans}
    selected_plan_id = st.selectbox(
        "选择开发计划",
        options=list(plan_options.keys()),
        format_func=lambda x: plan_options[x],
        index=list(plan_options.keys()).index(plan_id) if plan_id in plan_options else 0,
        key="comp_plan_select"
    )
    
    plan_spus = db.get_spus_by_plan(selected_plan_id)
    spu_options = {s["id"]: s["name"] for s in plan_spus} if plan_spus else {0: "全部SPU"}
    selected_spu_id = st.selectbox(
        "选择SPU（可选）",
        options=list(spu_options.keys()),
        format_func=lambda x: spu_options[x],
        key="comp_spu_select"
    )

# ===== 筛选 =====
competitors = db.get_competitors_by_plan_spu(selected_plan_id, selected_spu_id if selected_spu_id else 0)

fc1, fc2, fc3 = st.columns(3)
with fc1:
    platforms = ["全部"] + sorted(list(set(c["platform"] for c in competitors if c["platform"])))
    filter_platform = st.selectbox("按平台筛选", platforms, key="comp_platform")
with fc2:
    price_ranges = ["全部", "0-50", "50-100", "100-200", "200+"]
    filter_price = st.selectbox("按价格区间", price_ranges, key="comp_price")
with fc3:
    filter_key = st.selectbox("重点竞品", ["全部", "仅重点", "仅非重点"], key="comp_key")

filtered = competitors
if filter_platform != "全部":
    filtered = [c for c in filtered if c["platform"] == filter_platform]
if filter_price != "全部":
    lo, hi = filter_price.replace("+", "-99999").split("-")
    filtered = [c for c in filtered if float(lo) <= (c["price"] or 0) <= float(hi)]
if filter_key == "仅重点":
    filtered = [c for c in filtered if c["is_key"]]
elif filter_key == "仅非重点":
    filtered = [c for c in filtered if not c["is_key"]]

st.markdown(f"**共 {len(filtered)} 个竞品**")

# ===== 新增竞品 =====
if st.button("➕ 新增竞品", type="primary", key="add_comp", use_container_width=True):
    st.session_state["show_new_comp"] = True

if st.session_state.get("show_new_comp") or st.session_state.get("editing_comp"):
    is_edit = st.session_state.get("editing_comp") is not None
    edit_data = st.session_state.get("editing_comp")
    
    st.markdown("---")
    with st.form("comp_form", clear_on_submit=True):
        st.markdown("### 基本信息")
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            name = st.text_input("竞品名称 *", value=edit_data["name"] if is_edit else "")
            brand = st.text_input("品牌", value=edit_data["brand"] if is_edit else "")
            platform = st.selectbox("平台", ["淘宝", "京东", "拼多多", "亚马逊", "1688", "其他"],
                index=["淘宝","京东","拼多多","亚马逊","1688","其他"].index(edit_data["platform"]) if is_edit and edit_data["platform"] in ["淘宝","京东","拼多多","亚马逊","1688","其他"] else 0)
            price = st.number_input("售价（元）", min_value=0.0, value=float(edit_data["price"]) if is_edit else 0.0)
        with r1c2:
            link = st.text_input("链接", value=edit_data["link"] if is_edit else "")
            monthly_sales = st.text_input("月销量/销量参考", value=edit_data["monthly_sales"] if is_edit else "")
            is_key = st.checkbox("重点竞品", value=bool(edit_data["is_key"]) if is_edit else False)
        
        st.markdown("### 产品属性")
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            product_type = st.text_input("产品类型", value=edit_data["product_type"] if is_edit else "")
            material = st.text_input("材质", value=edit_data["material"] if is_edit else "")
            sizes = st.text_input("尺码", value=edit_data["sizes"] if is_edit else "")
        with r2c2:
            has_engraving = st.checkbox("支持刻字", value=bool(edit_data["has_engraving"]) if is_edit else False)
            has_locator = st.checkbox("支持定位器", value=bool(edit_data["has_locator"]) if is_edit else False)
        
        st.markdown("### 分析内容")
        selling_points = st.text_area("主要卖点", value=edit_data["selling_points"] if is_edit else "", height=60)
        pros = st.text_area("优点", value=edit_data["pros"] if is_edit else "", height=60)
        cons = st.text_area("缺点", value=edit_data["cons"] if is_edit else "", height=60)
        pain_points = st.text_area("差评痛点", value=edit_data["pain_points"] if is_edit else "", height=60)
        user_review_summary = st.text_area("用户评价摘要", value=edit_data["user_review_summary"] if is_edit else "", height=60)
        negative_review_reasons = st.text_area("差评原因", value=edit_data["negative_review_reasons"] if is_edit else "", height=60)
        qa_content = st.text_area("问大家内容摘要", value=edit_data["qa_content"] if is_edit else "", height=60)
        
        st.markdown("### 借鉴与风险")
        r3c1, r3c2 = st.columns(2)
        with r3c1:
            借鉴_points = st.text_area("可借鉴点", value=edit_data.get("借鉴_points","") if is_edit else "", height=60)
            our_opportunity = st.text_area("我们的优化机会", value=edit_data["our_opportunity"] if is_edit else "", height=60)
        with r3c2:
            避坑_points = st.text_area("避坑点", value=edit_data.get("避坑_points","") if is_edit else "", height=60)
            image_link = st.text_input("图片链接", value=edit_data["image_link"] if is_edit else "")
        
        notes = st.text_input("备注", value=edit_data["notes"] if is_edit else "")
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("取消", use_container_width=True)
        
        if submitted:
            data = {
                "plan_id": selected_plan_id, "spu_id": selected_spu_id if selected_spu_id else 0,
                "name": name, "brand": brand, "platform": platform, "link": link,
                "price": price, "monthly_sales": monthly_sales, "product_type": product_type,
                "material": material, "sizes": sizes, "has_engraving": has_engraving,
                "has_locator": has_locator, "selling_points": selling_points, "pros": pros,
                "cons": cons, "pain_points": pain_points, "user_review_summary": user_review_summary,
                "negative_review_reasons": negative_review_reasons, "qa_content": qa_content,
                "借鉴_points": 借鉴_points, "避坑_points": 避坑_points,
                "our_opportunity": our_opportunity, "image_link": image_link,
                "is_key": is_key, "notes": notes,
            }
            if is_edit:
                db.update_competitor(edit_data["id"], data)
                st.success("竞品已更新！")
                st.session_state.pop("editing_comp", None)
            else:
                db.create_competitor(data)
                st.success("竞品已添加！")
                st.session_state.pop("show_new_comp", None)
            st.rerun()
        
        if cancelled:
            st.session_state.pop("show_new_comp", None)
            st.session_state.pop("editing_comp", None)
            st.rerun()

# ===== 竞品列表（分区显示） =====
st.markdown("---")

if not filtered:
    st.info("暂无竞品数据，点击「新增竞品」开始录入")
else:
    # 价格分析
    with st.expander("📊 价格分析", expanded=False):
        prices = [c["price"] for c in filtered if c["price"]]
        if prices:
            st.markdown(f"- 最低价：¥{min(prices):.2f}")
            st.markdown(f"- 最高价：¥{max(prices):.2f}")
            st.markdown(f"- 平均价：¥{sum(prices)/len(prices):.2f}")
    
    for c in filtered:
        with st.container():
            cc1, cc2, cc3 = st.columns([3, 1, 1])
            with cc1:
                key_badge = "⭐ " if c["is_key"] else ""
                st.markdown(f"**{key_badge}{c['name']}**")
                st.caption(f"品牌: {c['brand']} | 平台: {c['platform']} | 💰 ¥{c['price']} | 销量: {c['monthly_sales']}")
                features = []
                if c["has_engraving"]: features.append("刻字")
                if c["has_locator"]: features.append("定位器")
                if features: st.caption(f"特性: {', '.join(features)}")
            with cc2:
                if c["selling_points"]:
                    st.caption(f"✅ {c['selling_points'][:50]}...")
            with cc3:
                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("✏️", key=f"edit_comp_{c['id']}", help="编辑"):
                        st.session_state["editing_comp"] = c
                        st.rerun()
                with ec2:
                    if st.button("🗑️", key=f"del_comp_{c['id']}"):
                        db.delete_competitor(c["id"])
                        st.success("已删除")
                        st.rerun()
            
            # 详情区域
            detail_cols = st.columns(3)
            with detail_cols[0]:
                if c["pros"]:
                    st.markdown(f"**✅ 优点：**\n{c['pros']}")
                if c["selling_points"]:
                    st.markdown(f"**🏷️ 卖点：**\n{c['selling_points']}")
            with detail_cols[1]:
                if c["cons"]:
                    st.markdown(f"**❌ 缺点：**\n{c['cons']}")
                if c["pain_points"]:
                    st.markdown(f"**💢 痛点：**\n{c['pain_points']}")
            with detail_cols[2]:
                if c.get("借鉴_points"):
                    st.markdown(f"**💡 可借鉴：**\n{c['借鉴_points']}")
                if c.get("避坑_points"):
                    st.markdown(f"**⚠️ 避坑：**\n{c['避坑_points']}")
            
            if c["our_opportunity"]:
                st.markdown(f"> 🚀 **我们的机会：** {c['our_opportunity']}")
            
            st.divider()
