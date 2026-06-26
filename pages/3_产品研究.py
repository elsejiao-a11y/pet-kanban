import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🔬 产品研究")

current_user = st.session_state.get("current_user", "阿豪")

# ===== 两个 Tab：竞品分析 & 产品需求 =====
tab1, tab2 = st.tabs(["🏷️ 竞品分析", "📝 产品需求"])

# ===== 竞品分析 Tab =====
with tab1:
    competitors = db.get_all_competitors()
    
    # 筛选
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
    
    # 新增竞品
    if st.button("➕ 新增竞品", type="primary", key="add_comp", use_container_width=True):
        st.session_state["show_new_comp"] = True
    
    if st.session_state.get("show_new_comp") or st.session_state.get("editing_comp"):
        is_edit = st.session_state.get("editing_comp") is not None
        edit_data = st.session_state.get("editing_comp")
        
        st.markdown("---")
        with st.form("comp_form", clear_on_submit=True):
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                name = st.text_input("竞品名称 *", value=edit_data["name"] if is_edit else "")
                brand = st.text_input("品牌", value=edit_data["brand"] if is_edit else "")
                platform = st.selectbox("平台", ["淘宝", "京东", "拼多多", "亚马逊", "1688", "其他"],
                                       index=["淘宝","京东","拼多多","亚马逊","1688","其他"].index(edit_data["platform"]) if is_edit and edit_data["platform"] in ["淘宝","京东","拼多多","亚马逊","1688","其他"] else 0)
                price = st.number_input("售价（元）", min_value=0.0, value=float(edit_data["price"]) if is_edit else 0.0)
                product_type = st.text_input("产品类型", value=edit_data["product_type"] if is_edit else "")
            with r1c2:
                link = st.text_input("链接", value=edit_data["link"] if is_edit else "")
                monthly_sales = st.text_input("月销量/销量参考", value=edit_data["monthly_sales"] if is_edit else "")
                image_link = st.text_input("图片链接", value=edit_data["image_link"] if is_edit else "")
                is_key = st.checkbox("重点竞品", value=bool(edit_data["is_key"]) if is_edit else False)
            
            selling_points = st.text_area("核心卖点", value=edit_data["selling_points"] if is_edit else "", height=60)
            pain_points = st.text_area("差评痛点", value=edit_data["pain_points"] if is_edit else "", height=60)
            our_opportunity = st.text_area("我们的优化机会", value=edit_data["our_opportunity"] if is_edit else "", height=60)
            notes = st.text_input("备注", value=edit_data["notes"] if is_edit else "")
            
            c1, c2, c3 = st.columns([1, 1, 3])
            with c1:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with c2:
                cancelled = st.form_submit_button("取消", use_container_width=True)
            
            if submitted:
                data = {
                    "name": name, "brand": brand, "platform": platform, "link": link,
                    "price": price, "monthly_sales": monthly_sales, "product_type": product_type,
                    "selling_points": selling_points, "pain_points": pain_points,
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
    
    # 竞品列表
    st.markdown("---")
    if not filtered:
        st.info("暂无竞品数据，点击「新增竞品」开始录入")
    else:
        for c in filtered:
            with st.container():
                cc1, cc2, cc3 = st.columns([3, 1, 1])
                with cc1:
                    key_badge = "⭐ " if c["is_key"] else ""
                    st.markdown(f"**{key_badge}{c['name']}**")
                    st.caption(f"品牌: {c['brand']} | 平台: {c['platform']} | 💰 ¥{c['price']} | 销量: {c['monthly_sales']}")
                with cc2:
                    if c["selling_points"]:
                        st.caption(f"✅ {c['selling_points'][:50]}...")
                    if c["pain_points"]:
                        st.caption(f"❌ {c['pain_points'][:50]}...")
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
                
                if c["our_opportunity"]:
                    st.markdown(f"> 💡 **优化机会：** {c['our_opportunity']}")
                st.divider()

# ===== 产品需求 Tab =====
with tab2:
    requirements = db.get_all_requirements()
    
    st.markdown("### 第一版产品需求清单")
    st.caption("注：AirTag 只能作为防丢定位器安装位，不能宣传为 GPS 实时定位")
    
    if st.button("➕ 新增需求", type="primary", key="add_req", use_container_width=True):
        st.session_state["show_new_req"] = True
    
    if st.session_state.get("show_new_req") or st.session_state.get("editing_req"):
        is_edit = st.session_state.get("editing_req") is not None
        edit_data = st.session_state.get("editing_req")
        
        st.markdown("---")
        with st.form("req_form", clear_on_submit=True):
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                requirement = st.text_input("产品需求 *", value=edit_data["requirement"] if is_edit else "")
                importance = st.selectbox("重要程度", ["高", "中", "低"],
                                         index=["高","中","低"].index(edit_data["importance"]) if is_edit and edit_data["importance"] in ["高","中","低"] else 0)
                owner = st.text_input("负责人", value=edit_data["owner"] if is_edit else "阿豪")
            with r1c2:
                must_have = st.checkbox("第一版必须做", value=bool(edit_data["must_have_v1"]) if is_edit else True)
                status = st.selectbox("状态", ["待定", "确认做", "确认不做", "待讨论"],
                                     index=["待定","确认做","确认不做","待讨论"].index(edit_data["status"]) if is_edit and edit_data["status"] in ["待定","确认做","确认不做","待讨论"] else 0)
            
            description = st.text_area("说明", value=edit_data["description"] if is_edit else "", height=60)
            final_decision = st.text_area("最终决定", value=edit_data["final_decision"] if is_edit else "", height=60)
            
            c1, c2, c3 = st.columns([1, 1, 3])
            with c1:
                submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
            with c2:
                cancelled = st.form_submit_button("取消", use_container_width=True)
            
            if submitted:
                data = {
                    "requirement": requirement, "importance": importance,
                    "must_have_v1": must_have, "description": description,
                    "final_decision": final_decision, "owner": owner, "status": status,
                }
                if is_edit:
                    db.update_requirement(edit_data["id"], data)
                    st.success("需求已更新！")
                    st.session_state.pop("editing_req", None)
                else:
                    db.create_requirement(data)
                    st.success("需求已添加！")
                    st.session_state.pop("show_new_req", None)
                st.rerun()
            if cancelled:
                st.session_state.pop("show_new_req", None)
                st.session_state.pop("editing_req", None)
                st.rerun()
    
    st.markdown("---")
    
    # 需求列表
    if requirements:
        # 按重要程度分组
        for imp in ["高", "中", "低"]:
            imp_reqs = [r for r in requirements if r["importance"] == imp]
            if not imp_reqs:
                continue
            imp_colors = {"高": "🔴", "中": "🟡", "低": "⚪"}
            st.markdown(f"#### {imp_colors[imp]} 重要程度：{imp}（{len(imp_reqs)}）")
            
            for r in imp_reqs:
                with st.container():
                    rc1, rc2, rc3 = st.columns([3, 1.5, 1])
                    with rc1:
                        v1_badge = "📌 V1必须 " if r["must_have_v1"] else ""
                        status_colors = {"待定": "⚪", "确认做": "🟢", "确认不做": "🔴", "待讨论": "🟡"}
                        st.markdown(f"**{r['req_no']} {r['requirement']}** {v1_badge}")
                        st.caption(f"{r['description']}")
                    with rc2:
                        sc = status_colors.get(r["status"], "⚪")
                        st.markdown(f"{sc} {r['status']}")
                        if r["final_decision"]:
                            st.caption(f"📋 {r['final_decision']}")
                    with rc3:
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            if st.button("✏️", key=f"edit_req_{r['id']}"):
                                st.session_state["editing_req"] = r
                                st.rerun()
                        with ec2:
                            if st.button("🗑️", key=f"del_req_{r['id']}"):
                                db.delete_requirement(r["id"])
                                st.success("已删除")
                                st.rerun()
                    st.divider()
    else:
        st.info("暂无产品需求")
