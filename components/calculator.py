import streamlit as st
import pandas as pd
from utils.db import fetch_materials
from utils.logic_engine import PricingEngine

def show_calculator(hourly_rate):
    st.header("Job Calculator")
    
    # Initialize Session State for Job Items if not exists
    if 'job_items' not in st.session_state:
        st.session_state.job_items = []

    # Init Engine
    materials_list = fetch_materials()
    # Create dict for PricingEngine {Name: Price}
    materials_dict = {m.get('name', 'Unknown'): m.get('cost_per_m2', 0.0) for m in materials_list}
    engine = PricingEngine(materials_dict, overhead_rate=hourly_rate)
    
    material_names = list(materials_dict.keys())

    # --- Section 1: Add Job Items ---
    st.subheader("1. Add Job Items")
    
    with st.expander("Add New Item", expanded=True):
        # Initialize unit defaults in session state if not present
        if 'w_unit' not in st.session_state:
            st.session_state.w_unit = "cm"
        if 'h_unit' not in st.session_state:
            st.session_state.h_unit = "cm"
            
        # Determine format based on unit (outside form to access session state)
        def get_format(unit):
            if unit in ['mm', 'cm']:
                return "%.0f"  # No decimals for mm/cm
            elif unit in ['m', 'ft', 'in']:
                return "%.2f"  # 2 decimals for m/ft/in
            return "%.3f"
        
        with st.form("add_item_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                # Default to first material if available for easier testing
                def_mat = [material_names[0]] if material_names else []
                # Multi-select for materials (e.g. Vinyl + Laminate)
                selected_materials = st.multiselect("Select Materials", options=material_names, default=def_mat, key="mat_multi")
            with col2:
                qty = st.number_input("Quantity", min_value=1, step=1, value=1, key="qty_input")
                
            c1, c2, c3, c4 = st.columns([2, 1, 2, 1])
            with c2:
                width_unit = st.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], key="w_unit")
            with c1:
                width_input = st.number_input("Width", min_value=0.0, format=get_format(st.session_state.w_unit), key="w_input")
            with c4:
                height_unit = st.selectbox("Unit", ["m", "cm", "mm", "ft", "in"], key="h_unit")
            with c3:
                height_input = st.number_input("Height", min_value=0.0, format=get_format(st.session_state.h_unit), key="h_input")
                
            add_btn = st.form_submit_button("Add Item to Quote")
            
        if add_btn and selected_materials and width_input > 0 and height_input > 0:
            # Convert to meters
            width_m = PricingEngine.convert_to_meters(width_input, width_unit)
            height_m = PricingEngine.convert_to_meters(height_input, height_unit)
            
            # Calculate item cost for display only (approx)
            item_rate = sum([materials_dict.get(m, 0) for m in selected_materials])
            area = width_m * height_m * qty
            item_cost = area * item_rate
            
            item = {
                "description": f"{', '.join(selected_materials)} ({width_input}{width_unit} x {height_input}{height_unit}) x{qty}",
                "materials": selected_materials, # List of names
                "width": width_m, # Store in meters for calc
                "height": height_m, # Store in meters for calc
                "qty": qty,
                "approx_cost": round(item_cost, 2)
            }
            st.session_state.job_items.append(item)
            st.success("Item added!")

    # Display Current Items
    if st.session_state.job_items:
        st.markdown("---")
        st.subheader("Current Job List")
        
        items_df = pd.DataFrame(st.session_state.job_items)
        st.dataframe(items_df[['description', 'approx_cost']], use_container_width=True)
        
        if st.button("Clear All Items"):
            st.session_state.job_items = []
            st.rerun()

    # --- Section 2: Labor Inputs ---
    st.markdown("---")
    st.subheader("2. Labor & Installation")
    
    l_col1, l_col2, l_col3 = st.columns(3)
    with l_col1:
        prod_hours = st.number_input("Production Hours", min_value=0.0, step=0.5)
    with l_col2:
        install_hours = st.number_input("Installation Hours", min_value=0.0, step=0.5)
    with l_col3:
        num_fitters = st.number_input("Number of Fitters", min_value=1, step=1, value=2)

    # --- Section 3: Results ---
    if st.session_state.job_items or prod_hours > 0:
        st.markdown("---")
        st.header("Quote Dashboard")
        
        # Calculate using Engine
        results = engine.calculate_job(
            st.session_state.job_items, 
            prod_hours, 
            install_hours, 
            installers=num_fitters
        )
        
        # Display Results
        m1, m2, m3 = st.columns(3)
        m1.metric("True Breakeven Cost", f"£{results['breakeven']:.2f}", help=f"Mat: {results['material_cost']:.2f} + Shop: {results['shop_cost']:.2f} + Install(Int): {results['install_cost_internal']:.2f}")
        m2.metric("Standard Quote", f"£{results['standard_price']:.2f}", delta=f"Profit: £{results['standard_profit']:.2f}")
        m3.metric("Premium Quote", f"£{results['premium_price']:.2f}", delta=f"Profit: £{results['premium_profit']:.2f}")
        
        # Visuals
        margin_percent = results['standard_profit'] / results['standard_price'] if results['standard_price'] > 0 else 0.0
        safe_progress = max(0.0, min(1.0, margin_percent))
        st.progress(safe_progress, text=f"Standard Margin Health ({margin_percent*100:.1f}%)")
        
        # Breakdown details
        with st.expander("See Cost Breakdown Details"):
            st.json(results)
