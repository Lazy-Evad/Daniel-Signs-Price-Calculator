import streamlit as st
import pandas as pd
from utils.db import fetch_materials, add_material, bulk_upload_materials

def show_supplier_manager():
    st.header("Supplier Manager")
    
    # --- Tabbed Interface for Supplier Actions ---
    tab1, tab2, tab3 = st.tabs(["View Materials", "Add Manually", "Bulk Upload"])
    
    # TAB 1: VIEW MATERIALS
    with tab1:
        st.subheader("Current Price List")
        materials = fetch_materials()
        
        if materials:
            df = pd.DataFrame(materials)
            # Reorder columns for display if keys exist, simply strictly for cleaner UI
            display_cols = ['name', 'cost_per_m2', 'roll_width', 'supplier']
            # Filter to only cols that exist in df
            final_cols = [c for c in display_cols if c in df.columns]
            
            st.dataframe(df[final_cols], use_container_width=True)
            st.caption(f"Total Items: {len(materials)}")
        else:
            st.info("No materials found in database.")

    # TAB 2: ADD MANUALLY
    with tab2:
        st.subheader("Add New Material")
        with st.form("add_material_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name", placeholder="e.g. Avery 800 Series")
                supplier = st.text_input("Supplier", placeholder="e.g. Spandex")
            with col2:
                cost = st.number_input("Cost per m² (£)", min_value=0.0, format="%.2f")
                width = st.number_input("Roll Width (m)", min_value=0.0, value=1.37, format="%.2f")
            
            submitted = st.form_submit_button("Add Material")
            
            if submitted:
                if name and cost > 0:
                    success = add_material(name, cost, width, supplier)
                    if success:
                        st.success(f"Added {name} successfully!")
                        st.rerun() # Refresh to show in list
                else:
                    st.error("Please enter a valid Name and Cost.")

    # TAB 3: BULK UPLOAD
    with tab3:
        st.subheader("Bulk Upload CSV")
        st.markdown("""
        **CSV Format Guide:**
        - Columns required: `Product`, `Price`, `Width`
        - Optional: `Supplier`
        """)
        
        uploaded_file = st.file_uploader("Upload Price List", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview:", df.head())
                
                # Basic validation
                required_cols = ['Product', 'Price', 'Width']
                if all(col in df.columns for col in required_cols):
                    if st.button("Confirm Upload"):
                        count = bulk_upload_materials(df)
                        st.success(f"Successfully uploaded {count} items!")
                        st.rerun()
                else:
                    st.error(f"CSV missing required columns: {required_cols}")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
