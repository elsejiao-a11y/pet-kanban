import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.markdown("# 🏭 打样生产")

current_user = st.session_state.get("current_user", "阿豪")
samples = db.get_all_samples()

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

# ===== 统计卡片 =====
if samples:
    s1, s2, s3, s4 = st.columns(4)
    total = len(samples)
    in_progress = len([s for s in samples if s["status"] in ("已下单", "打样中")])
    arrived = len([s for s in samples if s["status"] in ("已到样", "测试中")])
    passed = len([s for s in samples if s["status"] == "已通过"])
    
    with s1:
        st.metric("总样品数", total)
    with s2:
        st.metric("打样中", in_progress)
    with s3:
        st.metric("已到样/测试中", arrived)
    with s4:
        st.metric("已通过", passed)

st.markdown("---")

# ===== 新增样品 =====
if st.button("➕ 新增样品", type="primary", key="add_sample", use_container_width=True):
    st.session_state["show_new_sample"] = True

sample_statuses = ["未打样", "已下单", "打样中", "已到样", "测试中", "需修改", "已通过", "已淘汰"]

if st.session_state.get("show_new_sample") or st.session_state.get("editing_sample"):
    is_edit = st.session_state.get("editing_sample") is not None
    edit_data = st.session_state.get("editing_sample")
    
    st.markdown("---")
    with st.form("sample_form", clear_on_submit=True):
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            product_version = st.text_input("产品版本", value=edit_data["product_version"] if is_edit else "", placeholder="如：V1.0")
            supplier = st.text_input("供应商", value=edit_data["supplier"] if is_edit else "")
            sample_content = st.text_area("打样内容", value=edit_data["sample_content"] if is_edit else "", height=80)
            cost = st.number_input("打样成本（元）", min_value=0.0, value=float(edit_data["cost"]) if is_edit else 0.0)
        with r1c2:
            status = st.selectbox("状态", sample_statuses,
                                 index=sample_statuses.index(edit_data["status"]) if is_edit and edit_data["status"] in sample_statuses else 0)
            expected_date = st.date_input("预计到样时间", value=None)
            actual_date = st.date_input("实际到样时间", value=None)
            owner = st.selectbox("负责人", ["浩博", "阿豪", "潘翔"],
                                index=["浩博","阿豪","潘翔"].index(edit_data["owner"]) if is_edit and edit_data["owner"] in ["浩博","阿豪","潘翔"] else 0)
        
        test_result = st.text_area("测试结果", value=edit_data["test_result"] if is_edit else "", height=80,
                                   placeholder="记录各项测试的结果...")
        passed = st.checkbox("是否通过", value=bool(edit_data["passed"]) if is_edit else False)
        modification_notes = st.text_area("修改意见", value=edit_data["modification_notes"] if is_edit else "", height=60)
        
        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submitted = st.form_submit_button("💾 保存", type="primary", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("取消", use_container_width=True)
        
        if submitted:
            data = {
                "product_version": product_version, "supplier": supplier,
                "sample_content": sample_content, "cost": cost,
                "expected_date": expected_date.strftime("%Y-%m-%d") if expected_date else "",
                "actual_date": actual_date.strftime("%Y-%m-%d") if actual_date else "",
                "status": status, "test_result": test_result,
                "passed": passed, "modification_notes": modification_notes, "owner": owner,
            }
            if is_edit:
                db.update_sample(edit_data["id"], data)
                st.success(f"样品 {edit_data['sample_no']} 已更新！")
                st.session_state.pop("editing_sample", None)
            else:
                db.create_sample(data)
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
    # 按版本分组
    versions = sorted(list(set(s["product_version"] for s in samples if s["product_version"])))
    
    if len(versions) > 1:
        st.markdown("### 📊 版本对比")
        vcols = st.columns(min(len(versions), 4))
        for i, ver in enumerate(versions):
            with vcols[i % len(vcols)]:
                ver_samples = [s for s in samples if s["product_version"] == ver]
                total_cost = sum(s["cost"] for s in ver_samples)
                passed_count = len([s for s in ver_samples if s["passed"]])
                st.markdown(f"**{ver}**")
                st.caption(f"样品数：{len(ver_samples)}")
                st.caption(f"总打样费：¥{total_cost}")
                st.caption(f"已通过：{passed_count}/{len(ver_samples)}")
    
    st.markdown("---")
    st.markdown("### 📦 样品列表")
    
    for s in samples:
        status_colors = {
            "未打样": "#95A5A6", "已下单": "#3498DB", "打样中": "#2980B9",
            "已到样": "#27AE60", "测试中": "#F39C12", "需修改": "#E67E22",
            "已通过": "#2ECC71", "已淘汰": "#BDC3C7",
        }
        color = status_colors.get(s["status"], "#999")
        
        with st.container():
            sc1, sc2, sc3 = st.columns([3, 1.5, 1])
            with sc1:
                pass_badge = "✅" if s["passed"] else ("❌" if s["status"] == "已淘汰" else "")
                st.markdown(f"**{s['sample_no']} {s['product_version']}** {pass_badge}")
                st.caption(f"供应商: {s['supplier']} | 💰 ¥{s['cost']} | 👤 {s['owner']}")
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
                        db.delete_sample(s["id"])
                        st.success("已删除")
                        st.rerun()
            
            if s["test_result"]:
                st.markdown(f"> 📋 **测试结果：** {s['test_result']}")
            if s["modification_notes"]:
                st.markdown(f"> 🔧 **修改意见：** {s['modification_notes']}")
            st.divider()
