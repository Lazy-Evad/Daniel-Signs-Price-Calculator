import streamlit as st
from datetime import datetime
from utils.db import fetch_materials, save_job
from utils.logic_engine import PricingEngine
from utils.pdf_gen import generate_quote_pdf

# VERSION 4.0 - Production
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
            with st.form("add_material_form_v4", clear_on_submit=True):
                m_sel = st.multiselect("Select Materials", options=list(materials_dict.keys()), placeholder="Choose stock...")
                
                r_w1, r_w2 = st.columns(2)
                w_in = r_w1.number_input("Width", min_value=0.0)
                w_u = r_w2.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], index=1, key="mat_w_v4")
                
                # Height row
                r_h1, r_h2 = st.columns(2)
                h_in = r_h1.number_input("Height", min_value=0.0)
                h_u = r_h2.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], index=1, key="mat_h_v4")
                
                if st.form_submit_button("ADD MATERIAL TO JOB", use_container_width=True):
                    if m_sel and (w_in > 0 or h_in > 0):
                        st.session_state.job_items.append({
                            "type": "material",
                            "description": f"{', '.join(m_sel)} ({w_in}{w_u}x{h_in}{h_u})",
                            "raw_data": {
                                "width": PricingEngine.convert_to_meters(w_in, w_u), 
                                "height": PricingEngine.convert_to_meters(h_in, h_u), 
                                "qty": 1, 
                                "materials": m_sel
                            }
                        })
                        st.rerun()

        # Card: Add Labour
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">👷 LABOUR & INSTALLATION (LIVE)</div>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            p_h = l1.number_input("Production Hours", min_value=0.0, step=0.5, key="live_prod_h")
            i_h = l2.number_input("Installation Hours", min_value=0.0, step=0.5, key="live_inst_h")
            
            l3, l4 = st.columns(2)
            t_h = l3.number_input("Travel Hours", min_value=0.0, step=0.5, key="live_trav_h")
            fit = l4.number_input("Fitters (Qty)", min_value=0, value=1, key="live_fit_qty")
            
            st.caption("Lower section: Use 'Items' to list specific tasks if needed.")
            with st.form("add_labor_form_v4", clear_on_submit=True):
                l_desc = st.text_input("Optional: Addition Detail Label", placeholder="e.g. Extra design time")
                l_val = st.number_input("Hours", min_value=0.0, step=0.5)
                if st.form_submit_button("ADD ADDITIONAL LABOUR TO LIST", use_container_width=True):
                    if l_val > 0:
                        st.session_state.job_items.append({
                            "type": "labor",
                            "description": f"LABOUR: {l_desc or 'Additional'} ({l_val}h)",
                            "raw_labor": {"prod": l_val, "inst": 0, "trav": 0, "fit": 1}
                        })
                        st.rerun()

    with col_view:
        # Calculate Results (Live Inputs + Item List)
        calc_materials = [i["raw_data"] for i in st.session_state.job_items if i["type"] == "material"]
        tot_p = sum([i["raw_labor"]["prod"] for i in st.session_state.job_items if i["type"] == "labor"]) + p_h
        tot_i = sum([i["raw_labor"]["inst"] for i in st.session_state.job_items if i["type"] == "labor"]) + i_h
        tot_t = sum([i["raw_labor"]["trav"] for i in st.session_state.job_items if i["type"] == "labor"]) + t_h
        tot_f = max([i["raw_labor"]["fit"] for i in st.session_state.job_items if i["type"] == "labor"] + [fit])

        # Use markup_v4 from session state
        markup_val = st.session_state.get('markup_v4', 1.0)
        wastage_val = st.session_state.get('wastage_v4', 15.0)

        results = engine.calculate_job(
            calc_materials, tot_p, tot_i, 
            travel_hours=tot_t, installers=tot_f,
            wastage_percent=wastage_val,
            markup=markup_val
        )

        # Card: Summary
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📈 LIVE QUOTE SUMMARY</div>', unsafe_allow_html=True)
            
            # Quick Adjustments Row
            adj1, adj2 = st.columns(2)
            adj1.number_input("Material Wastage (%)", min_value=0.0, max_value=100.0, step=1.0, key="wastage_v4")
            adj2.slider("Markup Multiplier (x)", min_value=1.0, max_value=10.0, step=0.1, key="markup_v4")
            st.divider()

            m1, m2, m3 = st.columns(3)
            m1.metric("MAT. BASE COST", f"£{results['material_cost_total']:.2f}")
            m2.metric("TOTAL QUOTE", f"£{results['quote_price']:.2f}")
            m3.metric("EXPECTED PROFIT", f"£{results['profit']:.2f}")
            
            st.divider()
            
            # Internal Labour Cost (Breakeven) vs Billed Labour (Revenue)
            l_base = results['shop_cost_internal'] + results['install_cost_internal'] + results['travel_cost_internal']
            l_billed = results['labor_total_billed']
            
            col_l1, col_l2 = st.columns(2)
            col_l1.metric("LABOUR BASE COST", f"£{l_base:.2f}", help="Internal breakeven cost of your time (Overhead).")
            col_l2.metric("LABOUR BILLABLE", f"£{l_billed:.2f}", help="What you are charging the client for time.")
            
            margin = (results['profit'] / results['quote_price']) * 100 if results['quote_price'] > 0 else 0
            st.progress(max(0.0, min(1.0, margin/100)), text=f"Margin: {margin:.1f}%")

            st.divider()
            
            # --- PDF Export Action ---
            if results['quote_price'] > 0:
                try:
                    from io import BytesIO
                    import os
                    
                    # Generate PDF as bytes
                    pdf_bytes = generate_quote_pdf(client_info, st.session_state.job_items, results, markup_val)
                    
                    # Wrap in BytesIO for download button
                    pdf_buffer = BytesIO(pdf_bytes)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📄 DOWNLOAD PDF",
                            data=pdf_buffer,
                            file_name="Quote.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("💾 SAVE TO DESKTOP", use_container_width=True):
                            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "DanielSigns_Quote.pdf")
                            with open(desktop_path, "wb") as f:
                                f.write(pdf_bytes)
                            st.success(f"✅ Saved to Desktop!")
                    
                except Exception as e:
                    st.error(f"PDF Error: {str(e)}")
            else:
                st.button("📄 DOWNLOAD PDF QUOTE", disabled=True, use_container_width=True, help="Add items to create a quote first.")

        # Card: Job List
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📋 ITEMS</div>', unsafe_allow_html=True)
            
            # Display Live Labour & Installation Details at the top
            if p_h > 0 or i_h > 0 or t_h > 0:
                st.markdown("**LABOUR & INSTALLATION (LIVE)**")
                labour_details = []
                if p_h > 0:
                    labour_details.append(f"Production: {p_h}h")
                if i_h > 0:
                    labour_details.append(f"Installation: {i_h}h (x{fit} fitters)")
                if t_h > 0:
                    labour_details.append(f"Travel: {t_h}h")
                
                for detail in labour_details:
                    st.write(f"- {detail}")
                st.divider()
            
            # Display other job items
            if not st.session_state.job_items:
                if p_h == 0 and i_h == 0 and t_h == 0:
                    st.info("Empty")
            else:
                for idx, item in enumerate(st.session_state.job_items):
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{item['description']}**")
                    if c2.button("🗑️", key=f"del_v4_{idx}", use_container_width=True):
                        st.session_state.job_items.pop(idx); st.rerun()
                
                if st.button("🔥 CLEAR", key="clear_v4", use_container_width=True):
                    st.session_state.job_items = []; st.rerun()

    # Save
    if st.button("💾 SAVE ESTIMATE", key="save_v4", use_container_width=True):
        job_data = {
            "client": client_info, 
            "items": st.session_state.job_items, 
            "results": results, 
            "markup": markup_val,
            "version": "v4-final"
        }
        if save_job(job_data):
            st.balloons(); st.success("Saved!")
