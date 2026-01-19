import streamlit as st
from utils.db import fetch_materials, save_job
from utils.logic_engine import PricingEngine

# VERSION 2.3 - Pro Dashboard Layout
def show_calculator(hourly_rate, client_info=None):
    if 'job_items' not in st.session_state:
        st.session_state.job_items = []

    # Init Engine
    materials_dict = {m.get('name', 'Unknown'): m.get('cost_per_m2', 0.0) for m in fetch_materials()}
    engine = PricingEngine(
        materials_dict, 
        overhead_rate=st.session_state.hourly_rate,
        workshop_rate=st.session_state.workshop_rate,
        fitting_rate=st.session_state.fitting_rate,
        travel_rate=st.session_state.travel_rate
    )

    # --- TWO COLUMN GRID ---
    col_input, col_view = st.columns([1, 1], gap="medium")

    with col_input:
        # Card: Add Material
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">➕ ADD MATERIAL STOCK</div>', unsafe_allow_html=True)
            with st.form("add_material_form", clear_on_submit=True):
                m_sel = st.multiselect("Select Materials", options=list(materials_dict.keys()), placeholder="Choose stock...")
                
                r1_c1, r1_c2, r1_c3 = st.columns([1, 1.5, 1])
                qty = r1_c1.number_input("Qty", min_value=1, value=1)
                w_in = r1_c2.number_input("Width", min_value=0.0)
                w_u = r1_c3.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], key="mat_w_u")
                
                # Height row
                h, hu = st.columns([2.5, 1])
                h_in = h.number_input("Height", min_value=0.0)
                h_u = hu.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], key="mat_h_u")
                
                if st.form_submit_button("ADD MATERIAL TO JOB", use_container_width=True):
                    if m_sel and (w_in > 0 or h_in > 0):
                        st.session_state.job_items.append({
                            "type": "material",
                            "description": f"{', '.join(m_sel)} ({w_in}{w_u}x{h_in}{h_u}) x{qty}",
                            "raw_data": {
                                "width": PricingEngine.convert_to_meters(w_in, w_u), 
                                "height": PricingEngine.convert_to_meters(h_in, h_u), 
                                "qty": qty, 
                                "materials": m_sel
                            }
                        })
                        st.rerun()

        # Card: Add Labor
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">👷 LABOR & INSTALLATION</div>', unsafe_allow_html=True)
            with st.form("add_labor_form", clear_on_submit=True):
                l1, l2 = st.columns(2)
                p_h = l1.number_input("Production Hours", min_value=0.0, step=0.5)
                i_h = l2.number_input("Installation Hours", min_value=0.0, step=0.5)
                
                l3, l4 = st.columns(2)
                t_h = l3.number_input("Travel Hours", min_value=0.0, step=0.5)
                fit = l4.number_input("Fitters (Qty)", min_value=0, value=0)
                
                if st.form_submit_button("ADD LABOR TO JOB", use_container_width=True):
                    if p_h > 0 or i_h > 0 or t_h > 0:
                        st.session_state.job_items.append({
                            "type": "labor",
                            "description": f"LABOR: {p_h}h Prod, {i_h}h Inst (x{fit}), {t_h}h Trav",
                            "raw_labor": {"prod": p_h, "inst": i_h, "trav": t_h, "fit": fit}
                        })
                        st.rerun()

    with col_view:
        # Calculate Results
        calc_materials = [i["raw_data"] for i in st.session_state.job_items if i["type"] == "material"]
        tot_p = sum([i["raw_labor"]["prod"] for i in st.session_state.job_items if i["type"] == "labor"])
        tot_i = sum([i["raw_labor"]["inst"] for i in st.session_state.job_items if i["type"] == "labor"])
        tot_t = sum([i["raw_labor"]["trav"] for i in st.session_state.job_items if i["type"] == "labor"])
        tot_f = max([i["raw_labor"]["fit"] for i in st.session_state.job_items if i["type"] == "labor"] + [0])

        results = engine.calculate_job(
            calc_materials, tot_p, tot_i, 
            travel_hours=tot_t, installers=tot_f,
            wastage_percent=st.session_state.wastage_def,
            markup=st.session_state.markup_def
        )

        # Card: Summary
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📈 LIVE QUOTE SUMMARY</div>', unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            m1.metric("TOTAL QUOTE", f"£{results['quote_price']:.2f}")
            m2.metric("EXPECTED PROFIT", f"£{results['profit']:.2f}")
            
            margin = (results['profit'] / results['quote_price']) * 100 if results['quote_price'] > 0 else 0
            st.progress(max(0.0, min(1.0, margin/100)), text=f"Margin Health: {margin:.1f}%")

        # Card: Job List
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📋 CURRENT JOB ITEMS</div>', unsafe_allow_html=True)
            if not st.session_state.job_items:
                st.info("No items or labor added to this quote yet.")
            else:
                for idx, item in enumerate(st.session_state.job_items):
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{item['description']}**")
                    if c2.button("🗑️", key=f"del_{idx}", use_container_width=True):
                        st.session_state.job_items.pop(idx); st.rerun()
                
                st.divider()
                if st.button("🔥 CLEAR ENTIRE QUOTE", use_container_width=True):
                    st.session_state.job_items = []; st.rerun()

    # Full-Width Save Button (Primary Action)
    st.markdown('<div class="ds-primary">', unsafe_allow_html=True)
    if st.button("💾 PERMANENTLY SAVE ESTIMATE", key="save_final", use_container_width=True):
        job_data = {"client": client_info, "items": st.session_state.job_items, "results": results, "version": "v3-pro"}
        if save_job(job_data):
            st.balloons(); st.success("Estimate archived to History!")
    st.markdown('</div>', unsafe_allow_html=True)
