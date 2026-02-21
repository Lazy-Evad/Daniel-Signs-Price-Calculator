import streamlit as st
from datetime import datetime
from utils.db import fetch_materials, save_job
from utils.logic_engine import PricingEngine
from utils.nesting_optimizer import NestingOptimizer
from utils.pdf_gen import generate_quote_pdf

# VERSION 5.0 - Nesting Optimizer Edition
def show_calculator(hourly_rate, client_info=None):
    if 'job_items' not in st.session_state:
        st.session_state.job_items = []
    
    # Initialize nesting-specific session state
    if 'use_nesting' not in st.session_state:
        st.session_state.use_nesting = False
    if 'print_ready' not in st.session_state:
        st.session_state.print_ready = False
    if 'repeat_job' not in st.session_state:
        st.session_state.repeat_job = False
    if 'design_hours' not in st.session_state:
        st.session_state.design_hours = 0.0

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
        # Card: Add Material with Batch Nesting
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">➕ ADD MATERIAL (BATCH NESTING)</div>', unsafe_allow_html=True)
            
            # Nesting Toggle
            use_nesting = st.toggle("🎯 Enable Batch Nesting Optimizer", 
                                   value=st.session_state.use_nesting,
                                   help="Optimizes layout for multiple items to minimize waste",
                                   key="nesting_toggle")
            st.session_state.use_nesting = use_nesting
            
            with st.form("add_material_form_v5", clear_on_submit=True):
                m_sel = st.multiselect("Select Materials", options=list(materials_dict.keys()), 
                                      placeholder="Choose stock...")
                
                # Dimensions
                r_w1, r_w2 = st.columns(2)
                w_in = r_w1.number_input("Width", min_value=0.0, key="w_v5")
                w_u = r_w2.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], index=1, key="mat_w_v5")
                
                r_h1, r_h2 = st.columns(2)
                h_in = r_h1.number_input("Height", min_value=0.0, key="h_v5")
                h_u = r_h2.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], index=1, key="mat_h_v5")
                
                # Quantity (key for nesting!)
                qty = st.number_input("Quantity", min_value=1, value=1, step=1, 
                                    help="Number of identical items to produce")
                
                # Nesting-specific inputs (shown only if nesting enabled)
                if use_nesting:
                    st.divider()
                    st.caption("**Batch Nesting Parameters**")
                    
                    mat_w_val = st.number_input("Material Width (cm)", min_value=10.0, value=155.0, step=1.0,
                                              help="Available material width (max 160cm for vinyl)")
                    
                    col_b1, col_b2 = st.columns(2)
                    bleed = col_b1.number_input("Bleed (mm)", min_value=0.0, value=3.0, step=0.5)
                    gutter = col_b2.number_input("Gutter (mm)", min_value=0.0, value=5.0, step=1.0)
                
                if st.form_submit_button("CALCULATE & ADD MATERIAL", use_container_width=True):
                    if m_sel and (w_in > 0 or h_in > 0) and qty > 0:
                        # Convert to meters for storage
                        w_m = PricingEngine.convert_to_meters(w_in, w_u)
                        h_m = PricingEngine.convert_to_meters(h_in, h_u)
                        
                        item_data = {
                            "type": "material",
                            "width": w_m,
                            "height": h_m,
                            "qty": qty,
                            "materials": m_sel
                        }
                        
                        # Run nesting optimization if enabled
                        if use_nesting:
                            w_cm = NestingOptimizer.convert_to_cm(w_in, w_u)
                            h_cm = NestingOptimizer.convert_to_cm(h_in, h_u)
                            
                            nesting_result = NestingOptimizer.calculate_nesting(
                                w_cm, h_cm, qty, mat_w_val, 
                                bleed_mm=bleed, gutter_mm=gutter
                            )
                            
                            best = nesting_result['best_layout']
                            savings = nesting_result['savings']
                            
                            # Store optimized area instead of individual calculation
                            item_data['nesting_area_m2'] = best['total_area_m2']
                            item_data['nesting_result'] = nesting_result
                            item_data['description'] = (
                                f"{', '.join(m_sel)} | {qty}x {w_in}{w_u}×{h_in}{h_u} | "
                                f"NESTED: {best['orientation']} {best['layout_description']} | "
                                f"{best['total_area_m2']:.4f}m² | "
                                f"Eff: {best['efficiency_percent']:.1f}%"
                            )
                            
                            st.success(f"✅ Optimized! {best['orientation']} layout: "
                                     f"{best['efficiency_percent']:.1f}% efficient | "
                                     f"Saved {savings['waste_reduction_percent']:.1f}% waste vs individual")
                        else:
                            # Standard individual item
                            item_data['description'] = (
                                f"{', '.join(m_sel)} | {qty}x ({w_in}{w_u}×{h_in}{h_u})"
                            )
                        
                        st.session_state.job_items.append(item_data)
                        st.rerun()

        # Card: Job Settings (Print Ready, Repeat Job, Design Hours)
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📐 JOB SETTINGS</div>', unsafe_allow_html=True)
            
            pr_col, rj_col = st.columns(2)
            print_ready = pr_col.toggle("✅ Print Ready Artwork", 
                                       value=st.session_state.print_ready,
                                       help="Artwork is ready to print (no design work needed)")
            repeat_job = rj_col.toggle("🔄 Repeat Job", 
                                      value=st.session_state.repeat_job,
                                      help="Files already exist from previous job")
            
            st.session_state.print_ready = print_ready
            st.session_state.repeat_job = repeat_job
            
            # Design hours input (conditional display)
            if print_ready or repeat_job:
                st.info("ℹ️ Design time zeroed - artwork is ready or previously created")
                st.session_state.design_hours = 0.0
            else:
                design_h = st.number_input("Design/Artwork Hours", min_value=0.0, step=0.5,
                                          value=st.session_state.design_hours,
                                          help="Time for design, artwork prep, proofing")
                st.session_state.design_hours = design_h

        # Card: Labour & Installation
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">👷 LABOUR & INSTALLATION (LIVE)</div>', unsafe_allow_html=True)
            l1, l2 = st.columns(2)
            p_h = l1.number_input("Production Hours", min_value=0.0, step=0.5, key="live_prod_v5")
            i_h = l2.number_input("Installation Hours", min_value=0.0, step=0.5, key="live_inst_v5")
            
            l3, l4 = st.columns(2)
            t_h = l3.number_input("Travel Hours", min_value=0.0, step=0.5, key="live_trav_v5")
            fit = l4.number_input("Fitters (Qty)", min_value=0, value=1, key="live_fit_v5")
            
            st.caption("Lower section: Use 'Items' to list specific additional tasks if needed.")
            with st.form("add_labor_form_v5", clear_on_submit=True):
                l_desc = st.text_input("Optional: Additional Labour Label", placeholder="e.g. Site survey")
                l_val = st.number_input("Hours", min_value=0.0, step=0.5, key="extra_lab_v5")
                if st.form_submit_button("ADD ADDITIONAL LABOUR", use_container_width=True):
                    if l_val > 0:
                        st.session_state.job_items.append({
                            "type": "labor",
                            "description": f"LABOUR: {l_desc or 'Additional'} ({l_val}h)",
                            "raw_labor": {"prod": l_val, "inst": 0, "trav": 0, "fit": 1}
                        })
                        st.rerun()

    with col_view:
        # Calculate Results
        calc_materials = [i for i in st.session_state.job_items if i["type"] == "material"]
        tot_p = sum([i["raw_labor"]["prod"] for i in st.session_state.job_items if i["type"] == "labor"]) + p_h
        tot_i = sum([i["raw_labor"]["inst"] for i in st.session_state.job_items if i["type"] == "labor"]) + i_h
        tot_t = sum([i["raw_labor"]["trav"] for i in st.session_state.job_items if i["type"] == "labor"]) + t_h
        tot_f = max([i["raw_labor"]["fit"] for i in st.session_state.job_items if i["type"] == "labor"] + [fit])

        markup_val = st.session_state.get('markup_v5', 1.0)
        wastage_val = st.session_state.get('wastage_v5', 15.0)

        results = engine.calculate_job(
            calc_materials, tot_p, tot_i, 
            travel_hours=tot_t, installers=tot_f,
            wastage_percent=wastage_val,
            markup=markup_val,
            print_ready=st.session_state.print_ready,
            repeat_job=st.session_state.repeat_job,
            design_hours=st.session_state.design_hours,
            use_nesting=st.session_state.use_nesting
        )

        # Card: Summary
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📈 LIVE QUOTE SUMMARY</div>', unsafe_allow_html=True)
            
            # Job flags display
            flag_cols = st.columns(3)
            if results['print_ready']:
                flag_cols[0].markdown("✅ **Print Ready**")
            if results['repeat_job']:
                flag_cols[1].markdown("🔄 **Repeat Job**")
            if results['nesting_enabled']:
                flag_cols[2].markdown("🎯 **Nesting ON**")
            
            st.divider()
            
            # Quick Adjustments
            adj1, adj2 = st.columns(2)
            adj1.number_input("Material Wastage (%)", min_value=0.0, max_value=100.0, step=1.0, key="wastage_v5")
            adj2.slider("Markup Multiplier (x)", min_value=1.0, max_value=10.0, step=0.1, key="markup_v5")
            st.divider()

            m1, m2, m3 = st.columns(3)
            m1.metric("MAT. BASE COST", f"£{results['material_cost_total']:.2f}")
            m2.metric("TOTAL QUOTE", f"£{results['quote_price']:.2f}")
            m3.metric("EXPECTED PROFIT", f"£{results['profit']:.2f}")
            
            st.divider()
            
            # Design hours display
            if results['design_hours_input'] > 0:
                st.info(f"📐 Design Hours: {results['design_hours_input']:.1f}h → "
                       f"Billed: {results['design_hours_billed']:.1f}h")
            
            # Labour breakdown
            l_base = results['shop_cost_internal'] + results['install_cost_internal'] + results['travel_cost_internal']
            l_billed = results['labor_total_billed']
            
            col_l1, col_l2 = st.columns(2)
            col_l1.metric("LABOUR BASE COST", f"£{l_base:.2f}", help="Internal breakeven cost")
            col_l2.metric("LABOUR BILLABLE", f"£{l_billed:.2f}", help="What client pays")
            
            margin = (results['profit'] / results['quote_price']) * 100 if results['quote_price'] > 0 else 0
            st.progress(max(0.0, min(1.0, margin/100)), text=f"Margin: {margin:.1f}%")

            st.divider()
            
            # --- UNIT ECONOMICS (PER ITEM) ---
            # Extract total quantity from all material items
            total_quantity = sum([i['qty'] for i in calc_materials])
            
            if total_quantity > 0:
                # Use BILLABLE labour (matches the quote price breakdown)
                # Material (with markup) + Billable Labour = Quote Price
                labour_billed = results['labor_total_billed']
                # Internal/breakeven cost for reference
                labour_internal = (results['shop_cost_internal'] + 
                                   results['install_cost_internal'] + 
                                   results['travel_cost_internal'])
                
                # Per-item calculations (using billable rates to reconcile with quote price)
                material_per = round(results['material_cost_total'] / total_quantity, 2)
                labour_per   = round(labour_billed / total_quantity, 2)
                cost_per     = round(results['breakeven'] / total_quantity, 2)
                sell_per     = round(results['quote_price'] / total_quantity, 2)
                profit_per   = round(results['profit'] / total_quantity, 2)
                margin_per   = round((profit_per / sell_per * 100), 1) if sell_per > 0 else 0.0
                
                # % of total sell price
                mat_pct  = round((results['material_cost_total'] / results['quote_price'] * 100), 1) if results['quote_price'] > 0 else 0
                lab_pct  = round((labour_billed / results['quote_price'] * 100), 1) if results['quote_price'] > 0 else 0
                cost_pct = round((results['breakeven'] / results['quote_price'] * 100), 1) if results['quote_price'] > 0 else 0
                
                st.markdown(f'<div class="ds-card-header">💷 UNIT ECONOMICS (PER ITEM) — Qty: {total_quantity}</div>', 
                            unsafe_allow_html=True)
                
                st.caption("**Per-Item Breakdown (Billable Rates):**")
                
                # Header row
                h1, h2, h3, h4 = st.columns([3, 2, 2, 1.5])
                h1.markdown("**Component**")
                h2.markdown("**Per Item**")
                h3.markdown(f"**Total (×{total_quantity})**")
                h4.markdown("**% of Quote**")
                
                st.markdown("---")
                
                # Material row (includes wastage + markup)
                r1_1, r1_2, r1_3, r1_4 = st.columns([3, 2, 2, 1.5])
                r1_1.write("🧱 Material (inc. markup)")
                r1_2.write(f"£{material_per:.2f}")
                r1_3.write(f"£{results['material_cost_total']:.2f}")
                r1_4.write(f"{mat_pct:.1f}%")
                
                # Labour row (billable)
                r2_1, r2_2, r2_3, r2_4 = st.columns([3, 2, 2, 1.5])
                r2_1.write("👷 Labour (billable)")
                r2_2.write(f"£{labour_per:.2f}")
                r2_3.write(f"£{labour_billed:.2f}")
                r2_4.write(f"{lab_pct:.1f}%")
                
                st.markdown("---")
                
                # Cost to Produce row (internal breakeven)
                r3_1, r3_2, r3_3, r3_4 = st.columns([3, 2, 2, 1.5])
                r3_1.markdown("*Cost to Produce*")
                r3_2.markdown(f"*£{cost_per:.2f}*")
                r3_3.markdown(f"*£{results['breakeven']:.2f}*")
                r3_4.markdown(f"*{cost_pct:.1f}%*")
                
                # Sell Price row (bold)
                r4_1, r4_2, r4_3, r4_4 = st.columns([3, 2, 2, 1.5])
                r4_1.markdown("**Sell Price**")
                r4_2.markdown(f"**£{sell_per:.2f}**")
                r4_3.markdown(f"**£{results['quote_price']:.2f}**")
                r4_4.markdown("**100%**")
                
                st.markdown("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # Profit row
                r5_1, r5_2, r5_3, r5_4 = st.columns([3, 2, 2, 1.5])
                r5_1.markdown("**💰 Profit**")
                r5_2.markdown(f"**£{profit_per:.2f}**")
                r5_3.markdown(f"**£{results['profit']:.2f}**")
                r5_4.markdown(f"**{margin:.1f}%**")
                
                # Margin row
                r6_1, r6_2, r6_3, r6_4 = st.columns([3, 2, 2, 1.5])
                r6_1.markdown("**Margin**")
                r6_2.markdown(f"**{margin_per:.1f}%**")
                r6_3.markdown(f"**{margin:.1f}%**")
                r6_4.write("")
                
                st.caption("* Material includes wastage & markup. Labour uses billable rates. Cost to Produce = internal breakeven.")
            
            else:
                st.info("💷 Add materials with quantity to see per-item economics")
            
            st.divider()
            
            # PDF Export
            if results['quote_price'] > 0:
                try:
                    from io import BytesIO
                    import os
                    import re

                    # Capture timestamp & user at click time
                    now        = datetime.now()
                    user_name  = st.session_state.get('name', 'Unknown')

                    pdf_bytes  = generate_quote_pdf(
                        client_info,
                        st.session_state.job_items,
                        results,
                        markup_val,
                        created_by=user_name,
                        timestamp=now,
                        labour_hours={
                            'prod':    tot_p,
                            'inst':    tot_i,
                            'trav':    tot_t,
                            'design':  st.session_state.get('design_hours', 0.0),
                            'fitters': tot_f,
                        }
                    )
                    pdf_buffer = BytesIO(pdf_bytes)

                    # Build a clean filename: DanielSigns_Quote_ClientName_YYYY-MM-DD.pdf
                    safe_client = re.sub(r'[^\w\s-]', '', client_info.get('name', 'Client') or 'Client')
                    safe_client = re.sub(r'\s+', '_', safe_client.strip()) or 'Client'
                    pdf_filename = f"DanielSigns_Quote_{safe_client}_{now.strftime('%Y-%m-%d')}.pdf"

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📄 DOWNLOAD PDF",
                            data=pdf_buffer,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    with col2:
                        if st.button("💾 SAVE TO DESKTOP", use_container_width=True):
                            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", pdf_filename)
                            with open(desktop_path, "wb") as f:
                                f.write(pdf_bytes)
                            st.success(f"✅ Saved: {pdf_filename}")
                except Exception as e:
                    st.error(f"PDF Error: {str(e)}")
            else:
                st.button("📄 DOWNLOAD PDF", disabled=True, use_container_width=True)

        # Card: Nesting Analysis (if enabled and materials exist)
        if st.session_state.use_nesting and calc_materials:
            with st.container(border=True):
                st.markdown('<div class="ds-card-header">🎯 NESTING ANALYSIS</div>', unsafe_allow_html=True)
                
                for idx, item in enumerate(calc_materials):
                    if 'nesting_result' in item:
                        with st.expander(f"📊 {item['materials'][0]} (x{item['qty']})", expanded=(idx==0)):
                            result = item['nesting_result']
                            best = result['best_layout']
                            savings = result['savings']
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Orientation", best['orientation'])
                            col2.metric("Efficiency", f"{best['efficiency_percent']:.1f}%")
                            col3.metric("Waste Saved", f"{savings['waste_reduction_percent']:.1f}%")
                            
                            st.caption(f"**Layout:** {best['layout_description']}")
                            st.caption(f"**Material Size:** {best['material_width_cm']:.1f}cm × {best['material_length_cm']:.1f}cm")
                            st.caption(f"**Total Area:** {best['total_area_m2']:.4f} m²")

        # Card: Items List
        with st.container(border=True):
            st.markdown('<div class="ds-card-header">📋 ITEMS</div>', unsafe_allow_html=True)
            
            # Display Live Labour
            if p_h > 0 or i_h > 0 or t_h > 0 or st.session_state.design_hours > 0:
                st.markdown("**LABOUR & INSTALLATION (LIVE)**")
                labour_details = []
                if st.session_state.design_hours > 0 and results['design_hours_billed'] > 0:
                    labour_details.append(f"Design/Artwork: {results['design_hours_billed']}h")
                if p_h > 0:
                    labour_details.append(f"Production: {p_h}h")
                if i_h > 0:
                    labour_details.append(f"Installation: {i_h}h (x{fit} fitters)")
                if t_h > 0:
                    labour_details.append(f"Travel: {t_h}h")
                
                for detail in labour_details:
                    st.write(f"- {detail}")
                st.divider()
            
            # Display job items
            if not st.session_state.job_items:
                if p_h == 0 and i_h == 0 and t_h == 0:
                    st.info("Empty")
            else:
                for idx, item in enumerate(st.session_state.job_items):
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{item['description']}**")
                    if c2.button("🗑️", key=f"del_v5_{idx}", use_container_width=True):
                        st.session_state.job_items.pop(idx); st.rerun()
                
                if st.button("🔥 CLEAR", key="clear_v5", use_container_width=True):
                    st.session_state.job_items = []; st.rerun()

    # Save Button
    if st.button("💾 SAVE ESTIMATE", key="save_v5", use_container_width=True):
        job_data = {
            "client": client_info, 
            "items": st.session_state.job_items, 
            "results": results, 
            "markup": markup_val,
            "version": "v5-nesting"
        }
        if save_job(job_data):
            st.balloons(); st.success("Saved!")
